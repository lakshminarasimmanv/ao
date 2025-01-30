// this file can only have stable stuff! Akin to shim.h

#include <c10/util/BFloat16.h>
#include <c10/macros/Macros.h>     // used for C10_UID, verified to be header-only
#include <c10/core/DispatchKey.h>  // used for DispatchKey, enum verified to be header-only
#include <torch/csrc/inductor/aoti_torch/c/shim.h>

class StableLibrary final {
  public:
  // a pointer to a real Library
  // a kind
  enum Kind {
    DEF, // from TORCH_LIBRARY (no qualifier)
    IMPL,
    FRAGMENT,
  };


  // constructor

  
};


// _def function   ==> IGNORE LIBRARY + just call these

// stable_impl function (that takes in a string and a void** function pointer)
// _impl doesn't really need a Library object, try to avoid it for now
// just copy its implementation
// it'll give u a handle that needs to be kept alive, just assign to global for now


class StableTorchLibraryInit final {
  private:
    using InitFn = void(StableLibrary&);
    StableLibrary lib_;
  
  public:
    StableTorchLibraryInit(
      StableLibrary::Kind kind,
      InitFn* fn,
      const char* ns,
      std::optional<c10::DispatchKey> k,
      const char* file,
      uint32_t line)
      : lib_(kind, ns, k, file, line) {
        fn(lib_);
      }
};


#define STABLE_TORCH_LIBRARY_IMPL(ns, k, m) _STABLE_TORCH_LIBRARY_IMPL(ns, k, m, C10_UID)

#define _STABLE_TORCH_LIBRARY_IMPL(ns, k, m, uid)                         \
  static void C10_CONCATENATE(                                            \
      STABLE_TORCH_LIBRARY_IMPL_init_##ns##_##k##_, uid)(StableLibrary&);       \
  static const StableTorchLibraryInit C10_CONCATENATE(           \
      STABLE_TORCH_LIBRARY_IMPL_static_init_##ns##_##k##_, uid)(                 \
      StableLibrary::IMPL,                                               \
      &C10_CONCATENATE(STABLE_TORCH_LIBRARY_IMPL_init_##ns##_##k##_, uid), \
      #ns,                                                                \
      std::make_optional(c10::DispatchKey::k),                            \
      __FILE__,                                                           \
      __LINE__);                                                          \
  void C10_CONCATENATE(                                                   \
      STABLE_TORCH_LIBRARY_IMPL_init_##ns##_##k##_, uid)(StableLibrary & m)






// #define TORCH_LIBRARY_IMPL(ns, k, m) _TORCH_LIBRARY_IMPL(ns, k, m, C10_UID)

// #define _TORCH_LIBRARY_IMPL(ns, k, m, uid)                                \
//   static void TORCH_LIBRARY_IMPL_init_torchao_CUDA_uid(torch::Library&);       \
//   static const torch::detail::TorchLibraryInit      \
//       TORCH_LIBRARY_IMPL_static_init_torchao_CUDA_uid(                 \
//       torch::Library::IMPL,                                               \
//       (c10::impl::dispatch_key_allowlist_check(c10::DispatchKey::CUDA)       \
//            ? &TORCH_LIBRARY_IMPL_init_torchao_CUDA_uid \
//            : [](torch::Library&) -> void {}),                             \
//       torchao,                                                                \
//       std::make_optional(c10::DispatchKey::CUDA),                            \
//       __FILE__,                                                           \
//       __LINE__);                                                          \
//   TORCH_LIBRARY_IMPL_init_torchao_CUDA_uid(torch::Library & m) {

//   }

