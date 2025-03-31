#pragma once

#include "StaticSort.h"
#include <cutlass/arch/memory.h>
#include <cutlass/array.h>
#include <cutlass/bfloat16.h>
#include <cutlass/fast_math.h>
#include <cutlass/half.h>
#include <cutlass/integer_subbyte.h>

namespace torchao {

using cutlass::uint1b_t;
using cutlass::uint2b_t;
using cutlass::uint4b_t;
using uint8b_t = cutlass::integer_subbyte<8, false>;
using ReorderedLayoutInputE = cutlass::layout::ColumnMajorInterleaved<2>;
using ElementInputE = uint16_t;
constexpr int kWarpX = 4;
constexpr int kWarpY = 128;
constexpr int kThreadX = 1;
constexpr int kThreadY = 16;

// bitmask of selected values, in col-major storage
// eg: indices & (1 << col))
using Indices1x16 = uint16_t;

struct Tile2x16Masks {
  Indices1x16 a, b;
  CUTLASS_DEVICE Tile2x16Masks() { a = b = 0; }
};

static_assert(sizeof(Tile2x16Masks) == 4, "should be exactly uint32_t");

// Each thread has data for an 1x16 area of the input tensor
// 32 consecutive bits will live in a single thread
// of the metadata tensor will live in 4 different threads.
// This functions does the required warp shuffling to send data to the
// right threads.
// This took some time to write (and get right), hopefully these slides
// can help
// https://docs.google.com/presentation/d/1DtmKThv8S5QAyBktuLRYzZhRzCvS1qSkBbrqNCjMPeA/edit#slide=id.g249eb2e2f2e_0_28

// We want to write 64 bits at a time for the metadata
// 16 elements at 2 bits an element yields 32 bits -> so we write warp shuffle
// once and write for two threads.
// T0 T1 T2 T3 T4 T5 T6 T7
// T8
CUTLASS_DEVICE uint32_t warp_shuffle_meta(uint32_t meta_ab,
                                          bool transposed = false) {
  // FP8 format is different:
  // ['a[ 0,  0: 8]', 'a[ 0,  8:16]', 'a[ 0, 16:24]', 'a[ 0, 24:32]'] < T0
  // ['a[ 0, 32:40]', 'a[ 0, 40:48]', 'a[ 0, 48:56]', 'a[ 0, 56:64]']
  // ['a[ 1,  0: 8]', 'a[ 1,  8:16]', 'a[ 1, 16:24]', 'a[ 1, 24:32]']
  // ['a[ 1, 32:40]', 'a[ 1, 40:48]', 'a[ 1, 48:56]', 'a[ 1, 56:64]']
  // ['a[ 2,  0: 8]', 'a[ 2,  8:16]', 'a[ 2, 16:24]', 'a[ 2, 24:32]'] < T8
  // ['a[ 2, 32:40]', 'a[ 2, 40:48]', 'a[ 2, 48:56]', 'a[ 2, 56:64]']
  // ['a[ 3,  0: 8]', 'a[ 3,  8:16]', 'a[ 3, 16:24]', 'a[ 3, 24:32]']
  // ['a[ 3, 32:40]', 'a[ 3, 40:48]', 'a[ 3, 48:56]', 'a[ 3, 56:64]']

  // Use warp-shuffles to send data around threads
  bool thread_left = (threadIdx.y % 2) == 0;
  bool thread_bottom = threadIdx.x % 2;

  // This creates an array of 2 unsigned 8bit integers, correspoding
  // to a[0, 0:8] and a[0, 16:24]
  uint8b_t stage0_data[2] = {uint8b_t(meta_ab >> (8 * thread_left)),
                             uint8b_t(meta_ab >> (8 * (thread_left + 2)))};

  // shfl t0-t4 / t1-t5
  stage0_data[0] =
      __shfl_xor_sync(0xffffffff, stage0_data[0], transposed ? 1 : 4);
  stage0_data[1] =
      __shfl_xor_sync(0xffffffff, stage0_data[1], transposed ? 1 : 4);

  uint16_t line0 = int(uint8b_t(meta_ab >> (8 * (1 - thread_left))))
                   << ((1 - thread_left) * 8);
  line0 |= int(stage0_data[0]) << (thread_left * 8);

  uint16_t line1 = int(uint8b_t(meta_ab >> (8 * (1 - thread_left + 2))))
                   << ((1 - thread_left) * 8);
  line1 |= int(stage0_data[1]) << (thread_left * 8);

  uint16_t stage1_data = thread_bottom ? line0 : line1;
  stage1_data = __shfl_xor_sync(0xffffffff, stage1_data, transposed ? 4 : 1);

  uint32_t final_metadata;
  if (thread_bottom) {
    final_metadata = uint32_t(stage1_data) | uint32_t(line1) << 16;
  } else {
    final_metadata = uint32_t(stage1_data) << 16 | uint32_t(line0);
  }
  return final_metadata;
}

CUTLASS_DEVICE void warp_shuffle_and_write_meta(ElementInputE *metadata_duo,
                                                uint32_t meta_ab,
                                                bool transposed = false) {
  bool thread_left = (threadIdx.y % 2) == 0;
  bool thread_bottom = threadIdx.x % 2;

  if (transposed) {
    thread_left = (threadIdx.x % 2) == 0;
    thread_bottom = threadIdx.y % 2;
  }

  uint32_t final_metadata = warp_shuffle_meta(meta_ab, transposed);

  int index = (!thread_left + 2 * thread_bottom) * 4;
  ((uint32_t *)metadata_duo)[index] = final_metadata;
}

template <typename Element_> struct KernelTypes {
  using Element = Element_;
  using Fragment =
      cutlass::Array<Element, 16>; // always read from gmem in chunks of 128bits
  using Fragment8 = cutlass::Array<Element, 8>;

  struct Params {
    /// inputs
    Element const *input;
    int64_t input_s0;
    int64_t input_dim0;
    int64_t input_dim1;

    /// outputs
    Element *packed;
    int64_t packed_stride;

    Element *packed_trans;
    int64_t packed_trans_stride;

    uint64_t *threads_masks;

    __host__ dim3 getBlocksGrid() const {
      return dim3(cutlass::ceil_div(input_dim0, kWarpX),
                  cutlass::ceil_div(input_dim1, kWarpY), 1);
    }

    static CUTLASS_HOST_DEVICE dim3 getThreadsGrid() {
      return dim3(kWarpX / kThreadX, kWarpY / kThreadY, 1);
    }

    CUTLASS_DEVICE Tile2x16Masks *getCurrentThreadIndices() const {
      Tile2x16Masks *gmem_threads_masks = (Tile2x16Masks *)threads_masks;
      gmem_threads_masks += blockIdx.y * getThreadsGrid().y + threadIdx.y;
      int64_t strideX = gridDim.y * getThreadsGrid().y;
      gmem_threads_masks +=
          (blockIdx.x * getThreadsGrid().x + threadIdx.x) * strideX;
      return gmem_threads_masks;
    }
  };

  // Holds the packed values for a 1x4 segment (2 values)
  struct Strip1x4Packed {
    Element values[2];
    CUTLASS_DEVICE Strip1x4Packed() {
      values[0] = Element(0);
      values[1] = Element(0);
    }
  };

  // Holds the packed values for a 1x16 Tile (4 1x4 segments)
  struct Strip1x16Packed {
    Strip1x4Packed strips[4];
    CUTLASS_DEVICE Strip1x16Packed() {
      strips[0] = Strip1x4Packed();
      strips[1] = Strip1x4Packed();
      strips[2] = Strip1x4Packed();
      strips[3] = Strip1x4Packed();
    }
  };

  struct Tile2x16Meta {
    uint32_t meta_ab;
    uint32_t meta_ab_trans;

    CUTLASS_DEVICE Tile2x16Meta() { meta_ab = meta_ab_trans = 0; }
  };

  CUTLASS_DEVICE static void writePacked(Element *ptr, Strip1x16Packed packed) {
    Fragment8 write;
    write[0] = packed.strips[0].values[0];
    write[1] = packed.strips[0].values[1];
    write[2] = packed.strips[1].values[0];
    write[3] = packed.strips[1].values[1];
    write[4] = packed.strips[2].values[0];
    write[5] = packed.strips[2].values[1];
    write[6] = packed.strips[3].values[0];
    write[7] = packed.strips[3].values[1];
    cutlass::arch::global_store<Fragment8, sizeof(Fragment8)>(write, ptr, true);
  }

  struct Tile1x16Accessor {
    using Element = Element_;

    Fragment (&_lines)[2];
    int _start_row;
    int _start_col;

    CUTLASS_DEVICE Tile1x16Accessor(Fragment (&lines)[2], int start_row,
                                    int start_col)
        : _lines(lines), _start_row(start_row), _start_col(start_col) {}

    CUTLASS_DEVICE typename Fragment::reference at(int r, int c) {
      return _lines[r + _start_row][c + _start_col];
    }
  };

  CUTLASS_DEVICE static Strip1x16Packed pack_1x16(Indices1x16 indices,
                                                  Tile1x16Accessor tile,
                                                  uint32_t &meta, int meta_pos,
                                                  bool print) {
    Strip1x16Packed packed;
    CUTLASS_PRAGMA_UNROLL
    for (int strip = 0; strip < 4; ++strip) {
      uint2b_t col0_from, col1_from;
      auto packValue = [&](uint2b_t col_to, uint2b_t col_from) {
        auto value = tile.at(0, (4 * strip + col_from)).get();
        packed.strips[strip].values[col_to] = value;
        if (col_to == uint2b_t(0)) {
          col0_from = col_from;
        } else {
          col1_from = col_from;
        }
      };

      auto isSelected = [&](int col) {
        return indices & (1 << (4 * strip) + col);
      };

      if (isSelected(1)) {
        packValue(0, 1);
      }
      if (isSelected(0)) {
        packValue(0, 0);
      }
      if (isSelected(0) && isSelected(1)) {
        packValue(1, 1);
      }
      // Process cols 2/3
      // same sort of heuristic
      if (isSelected(2)) {
        packValue(1, 2);
      }
      if (isSelected(3)) {
        packValue(1, 3);
      }
      if (isSelected(2) && isSelected(3)) {
        packValue(0, 2);
      }
      // this needs to be changed and can probably be moved out of the for loop
      int add_mask = (col0_from | (col1_from << 2)) << (4 * strip + meta_pos);
      meta |= add_mask;
    }
    return packed;
  }

  // this kernel is for a single thread
  template <typename Algorithm, typename MetadataStore>
  CUTLASS_DEVICE static void
  sparse_semi_structured_tile_kernel(Params p, MetadataStore metadata_gmem,
                                     Algorithm compute_tile_indices) {
    // Each thread is responsible for an 1x16 tile, which contains 4 1x4 tiles:
    // A, B, C and D, as displayed in the following schema:
    // +---+---+---+---+
    // | A | B | C | D |
    // +---+---+---+---+
    // Each warp (32 threads) will then be responsible for a 4x128 tile of the
    // input.
    // This configuration allows to read/write data in 128bits chunks. These
    // memory accesses are coalesced at the warp-level into 128bytes. See also:
    // https://docs.google.com/presentation/d/1DtmKThv8S5QAyBktuLRYzZhRzCvS1qSkBbrqNCjMPeA/edit#slide=id.g2494f30c7cf_0_0

    // Top-left of the 8x8 tile we own
    int warp_x = blockIdx.x * kWarpX;
    int warp_y = blockIdx.y * kWarpY;
    int x = warp_x + threadIdx.x * kThreadX;
    int y = warp_y + threadIdx.y * kThreadY;
    bool debug = (blockIdx.x == 0 && blockIdx.y == 0 && threadIdx.x == 1 &&
                  threadIdx.y == 0);

    Element const *input = p.input + x * p.input_s0 + y;
    Element *packed = p.packed + x * p.packed_stride + (y / 2);
    Element *packed_trans =
        p.packed_trans + (x / 2) + y * p.packed_trans_stride;

    Fragment lines[2]; // Contains all values from the 2x16 tile

    Tile2x16Meta metadata;
    Tile2x16Masks indices;

    // Load/process tiles `A` and `B`
    Element fillValue = Algorithm::template outOfBoundsFillValue<Element>();
    CUTLASS_PRAGMA_UNROLL
    for (int i = 0; i < 2; ++i) {
      lines[i].fill(fillValue);
      cutlass::arch::global_load<Fragment, sizeof(Fragment)>(
          lines[i], input + i * p.input_s0, x + i < p.input_dim0);
    }

    indices.a = compute_tile_indices(Tile1x16Accessor(lines, 0, 0));
    indices.b = compute_tile_indices(Tile1x16Accessor(lines, 1, 0));
    Strip1x16Packed packed_a = pack_1x16(
        indices.a, Tile1x16Accessor(lines, 0, 0), metadata.meta_ab, 0, debug);
    Strip1x16Packed packed_b = pack_1x16(
        indices.b, Tile1x16Accessor(lines, 1, 0), metadata.meta_ab, 16, debug);
    writePacked(packed, packed_a);

    *p.getCurrentThreadIndices() = indices;

    // Writing meta non-transposed
    {
      ElementInputE *packed_meta_reordered = metadata_gmem.get_metaN(
          warp_x, threadIdx.x * kThreadX, warp_y, threadIdx.y * kThreadY);
      warp_shuffle_and_write_meta(packed_meta_reordered, metadata.meta_ab);
    }

    // indices.b = compute_tile_indices(Tile1x16Accessor(lines, 1, 0));
    char binary_a[17] = {0}; // 16 bits + null terminator
    char binary_b[17] = {0}; // 16 bits + null terminator

    char meta_a[33] = {0};

    //--------------------------- DEBUG -----------------------------------
    // Build binary string for indices.a
    for (int bit = 15; bit >= 0; bit--) {
      binary_a[15 - bit] = (indices.a & (1 << bit)) ? '1' : '0';
    }

    // Build binary string for metadata.meta_a
    for (int bit = 31; bit >= 0; bit--) {
      meta_a[31 - bit] = (metadata.meta_ab & (1 << bit)) ? '1' : '0';
    }

    // Build binary string for indices.b
    for (int bit = 15; bit >= 0; bit--) {
      binary_b[15 - bit] = (indices.b & (1 << bit)) ? '1' : '0';
    }

    if (blockIdx.x == 0 && blockIdx.y == 0) {
      // Assuming packed_a.values is an array of 8 values (corresponding to the
      // 8 selected positions)
      printf(
          "Debug info: blockIdx=(%d,%d), threadIdx=(%d,%d), warp_xy=(%d,%d), "
          "xy=(%d,%d), indices.a=%s, indices.b=%s, "
          "meta_a=%s, meta_b=%d, "
          "packed_a=[%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f]\n",
          blockIdx.x, blockIdx.y, threadIdx.x, threadIdx.y, warp_x, warp_y, x,
          y, binary_a, binary_b, meta_a, metadata.meta_ab, (float)packed[0],
          (float)packed[1], (float)packed[2], (float)packed[3],
          (float)packed[4], (float)packed[5], (float)packed[6],
          (float)packed[7]);
    }
  }
};

} // namespace torchao
