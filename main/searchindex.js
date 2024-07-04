Search.setIndex({"docnames": ["api_ref_dtypes", "api_ref_intro", "api_ref_kernel", "api_ref_quantization", "api_ref_sparsity", "dtypes", "generated/torchao.dtypes.AffineQuantizedTensor", "generated/torchao.dtypes.to_affine_quantized", "generated/torchao.dtypes.to_nf4", "generated/torchao.quantization.Int4WeightOnlyGPTQQuantizer", "generated/torchao.quantization.Int4WeightOnlyQuantizer", "generated/torchao.quantization.SmoothFakeDynQuantMixin", "generated/torchao.quantization.SmoothFakeDynamicallyQuantizedLinear", "generated/torchao.quantization.int4_weight_only", "generated/torchao.quantization.int8_dynamic_activation_int4_weight", "generated/torchao.quantization.int8_dynamic_activation_int8_weight", "generated/torchao.quantization.int8_weight_only", "generated/torchao.quantization.smooth_fq_linear_to_inference", "generated/torchao.quantization.swap_linear_with_smooth_fq_linear", "generated/torchao.sparsity.PerChannelNormObserver", "generated/torchao.sparsity.WandaSparsifier", "generated/torchao.sparsity.apply_fake_sparsity", "generated/torchao.sparsity.apply_sparse_semi_structured", "getting-started", "index", "overview", "performant_kernels", "quantization", "sg_execution_times", "sparsity", "tutorials/index", "tutorials/sg_execution_times", "tutorials/template_tutorial"], "filenames": ["api_ref_dtypes.rst", "api_ref_intro.rst", "api_ref_kernel.rst", "api_ref_quantization.rst", "api_ref_sparsity.rst", "dtypes.rst", "generated/torchao.dtypes.AffineQuantizedTensor.rst", "generated/torchao.dtypes.to_affine_quantized.rst", "generated/torchao.dtypes.to_nf4.rst", "generated/torchao.quantization.Int4WeightOnlyGPTQQuantizer.rst", "generated/torchao.quantization.Int4WeightOnlyQuantizer.rst", "generated/torchao.quantization.SmoothFakeDynQuantMixin.rst", "generated/torchao.quantization.SmoothFakeDynamicallyQuantizedLinear.rst", "generated/torchao.quantization.int4_weight_only.rst", "generated/torchao.quantization.int8_dynamic_activation_int4_weight.rst", "generated/torchao.quantization.int8_dynamic_activation_int8_weight.rst", "generated/torchao.quantization.int8_weight_only.rst", "generated/torchao.quantization.smooth_fq_linear_to_inference.rst", "generated/torchao.quantization.swap_linear_with_smooth_fq_linear.rst", "generated/torchao.sparsity.PerChannelNormObserver.rst", "generated/torchao.sparsity.WandaSparsifier.rst", "generated/torchao.sparsity.apply_fake_sparsity.rst", "generated/torchao.sparsity.apply_sparse_semi_structured.rst", "getting-started.rst", "index.rst", "overview.rst", "performant_kernels.rst", "quantization.rst", "sg_execution_times.rst", "sparsity.rst", "tutorials/index.rst", "tutorials/sg_execution_times.rst", "tutorials/template_tutorial.rst"], "titles": ["torchao.dtypes", "<code class=\"docutils literal notranslate\"><span class=\"pre\">torchao</span></code> API Reference", "torchao.kernel", "torchao.quantization", "torchao.sparsity", "Dtypes", "AffineQuantizedTensor", "to_affine_quantized", "to_nf4", "Int4WeightOnlyGPTQQuantizer", "Int4WeightOnlyQuantizer", "SmoothFakeDynQuantMixin", "SmoothFakeDynamicallyQuantizedLinear", "int4_weight_only", "int8_dynamic_activation_int4_weight", "int8_dynamic_activation_int8_weight", "int8_weight_only", "smooth_fq_linear_to_inference", "swap_linear_with_smooth_fq_linear", "PerChannelNormObserver", "WandaSparsifier", "apply_fake_sparsity", "apply_sparse_semi_structured", "Getting Started", "Welcome to the torchao Documentation", "Overview", "Performant Kernels", "Quantization", "Computation times", "Sparsity", "&lt;no title&gt;", "Computation times", "Template Tutorial"], "terms": {"thi": [1, 6, 12, 13, 14, 19, 20, 21, 32], "section": 1, "introduc": 1, "dive": 1, "detail": 1, "how": [1, 6, 13], "integr": 1, "pytorch": [1, 24, 32], "optim": 1, "your": [1, 24], "machin": 1, "learn": [1, 13, 32], "model": [1, 14, 17, 18, 20, 21, 22, 24], "sparsiti": [1, 19, 20, 21, 22, 24], "quantiz": [1, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24], "dtype": [1, 6, 7, 8, 24], "kernel": [1, 6, 13], "tba": [2, 5, 23, 25, 26, 27, 29], "class": [6, 9, 10, 11, 12, 19, 20], "torchao": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22], "layout_tensor": 6, "aqtlayout": 6, "block_siz": [6, 7, 8], "tupl": [6, 7, 20], "int": [6, 7, 8, 10, 20], "shape": 6, "size": [6, 13, 14], "quant_min": [6, 7], "option": [6, 7, 10, 17, 18, 20], "none": [6, 7, 17, 18, 20], "quant_max": [6, 7], "zero_point_domain": [6, 7, 13], "zeropointdomain": [6, 7, 13], "stride": 6, "sourc": [6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 30, 32], "affin": 6, "tensor": [6, 7, 8, 13, 20, 32], "subclass": [6, 12, 19], "mean": 6, "we": 6, "float": [6, 7, 13, 18, 20], "point": [6, 13], "an": [6, 20, 24], "transform": 6, "quantized_tensor": 6, "float_tensor": 6, "scale": [6, 11, 12, 17, 18], "zero_point": [6, 13], "The": [6, 17, 18, 20], "repres": [6, 20], "look": 6, "extern": 6, "regardless": 6, "intern": 6, "represent": [6, 13], "s": 6, "type": [6, 9, 10, 13], "orient": 6, "field": 6, "serv": 6, "gener": [6, 30, 32], "layout": [6, 13], "storag": 6, "data": 6, "e": 6, "g": 6, "store": [6, 19], "plain": [6, 7], "int_data": 6, "pack": 6, "format": 6, "depend": 6, "devic": [6, 9, 10], "oper": 6, "granular": [6, 13, 14], "element": 6, "share": 6, "same": 6, "qparam": 6, "when": 6, "input": [6, 20], "dimens": 6, "ar": [6, 13, 20], "us": [6, 13, 14, 20, 21, 24], "per": [6, 12, 13, 14, 15, 16, 20], "torch": [6, 12, 13, 17, 18, 21, 32], "minimum": 6, "valu": [6, 11, 12, 17, 20], "specifi": [6, 20], "deriv": 6, "from": [6, 14, 28, 31, 32], "maximum": [6, 17], "domain": [6, 13], "should": [6, 12, 19, 20], "eitehr": 6, "integ": [6, 13], "zero": [6, 13, 20], "ad": [6, 20], "dure": [6, 18], "subtract": 6, "unquant": 6, "default": [6, 17, 18], "input_quant_func": 6, "callabl": 6, "function": [6, 12, 19, 20, 21, 24], "object": 6, "take": [6, 12, 19], "output": [6, 32], "float32": 6, "dequant": [6, 13], "given": 6, "return": [6, 17, 18], "arg": [6, 11, 12, 20], "kwarg": [6, 11, 12, 19, 20, 21, 22], "perform": [6, 11, 12, 17, 19], "convers": 6, "A": [6, 19], "infer": [6, 12, 17], "argument": 6, "self": [6, 11, 12], "If": [6, 17, 20], "alreadi": 6, "ha": 6, "correct": 6, "otherwis": 6, "copi": [6, 20], "desir": 6, "here": 6, "wai": 6, "call": [6, 12, 19], "non_block": 6, "fals": [6, 13, 17, 20], "memory_format": 6, "preserve_format": 6, "memori": 6, "tri": 6, "convert": [6, 12], "asynchron": 6, "respect": 6, "host": 6, "possibl": 6, "cpu": 6, "pin": 6, "cuda": [6, 9, 10], "set": [6, 11, 12, 17, 20], "new": 6, "creat": 6, "even": 6, "match": 6, "other": [6, 20, 32], "exampl": [6, 20, 28, 30, 31, 32], "randn": 6, "2": [6, 13, 21, 32], "initi": 6, "float64": 6, "0": [6, 9, 11, 12, 18, 20, 28, 31, 32], "5044": 6, "0005": 6, "3310": 6, "0584": 6, "cuda0": 6, "true": [6, 7, 9, 10, 17], "input_float": 7, "mapping_typ": 7, "mappingtyp": 7, "target_dtyp": 7, "ep": 7, "scale_dtyp": 7, "zero_point_dtyp": 7, "preserve_zero": [7, 13], "bool": [7, 10, 17], "extended_layout": 7, "str": [7, 18, 20], "inner_k_til": [7, 9, 10, 13], "64": [8, 9, 13], "scaler_block_s": 8, "256": [8, 10, 13], "blocksiz": 9, "128": [9, 13], "percdamp": 9, "01": 9, "groupsiz": [9, 10], "8": [9, 10, 13], "padding_allow": [9, 10], "set_debug_x_absmax": [11, 12], "x_running_abs_max": [11, 12], "which": [11, 12], "lead": [11, 12], "smooth": [11, 12], "all": [11, 12, 19, 20, 21, 28, 30], "ones": [11, 12, 20], "alpha": [11, 12, 18], "5": [11, 12, 18, 20, 32], "enabl": [11, 12], "benchmark": [11, 12, 17], "without": [11, 12], "calibr": [11, 12], "replac": [12, 18], "nn": [12, 17, 18], "linear": [12, 13, 14, 15, 16, 18, 21], "implement": 12, "dynam": [12, 14, 15], "token": [12, 14, 15], "activ": [12, 14, 15, 17, 20], "channel": [12, 15, 16, 19], "weight": [12, 13, 14, 15, 16, 20], "base": [12, 20], "smoothquant": [12, 17, 18], "forward": [12, 19], "x": [12, 32], "defin": [12, 19, 20], "comput": [12, 19, 20], "everi": [12, 19], "overridden": [12, 19], "although": [12, 19], "recip": [12, 19], "pass": [12, 19], "need": [12, 19, 20], "within": [12, 19], "one": [12, 19], "modul": [12, 17, 18, 19, 20], "instanc": [12, 19], "afterward": [12, 19], "instead": [12, 13, 19], "sinc": [12, 19], "former": [12, 19], "care": [12, 19], "run": [12, 17, 19, 32], "regist": [12, 19], "hook": [12, 19], "while": [12, 19, 20], "latter": [12, 19], "silent": [12, 19], "ignor": [12, 19], "them": [12, 19], "classmethod": 12, "from_float": 12, "mod": 12, "fake": 12, "version": 12, "note": [12, 20], "requir": 12, "to_infer": 12, "calcul": [12, 17], "prepar": [12, 17, 20], "group_siz": [13, 14], "appli": [13, 14, 15, 16], "uint4": 13, "onli": [13, 16], "asymmetr": [13, 14], "group": [13, 14], "layer": [13, 15, 16, 17, 18, 20, 21], "tensor_core_til": 13, "speedup": 13, "tinygemm": 13, "target": [13, 20], "int4mm": 13, "op": 13, "aten": 13, "_weight_int4pack_mm": 13, "main": 13, "differ": 13, "algorithm": 13, "compar": [13, 20], "more": [13, 14, 24], "tradit": 13, "follow": 13, "1": [13, 20, 28, 31, 32], "doe": 13, "have": [13, 20], "exactli": 13, "choose_qparams_affin": 13, "pleas": 13, "relev": [13, 32], "code": [13, 30, 32], "quantize_affin": 13, "dequantize_affin": 13, "about": 13, "paramet": [13, 14, 17, 18, 20], "chosen": 13, "control": [13, 14, 20], "smaller": [13, 14], "fine": [13, 14], "grain": [13, 14], "choic": 13, "32": [13, 14], "int4": [13, 14], "mm": 13, "4": [13, 21], "int8": [14, 15, 16], "symmetr": [14, 15, 16], "produc": 14, "executorch": 14, "backend": 14, "current": [14, 18, 20], "did": 14, "support": 14, "lower": 14, "flow": [14, 21], "yet": 14, "debug_skip_calibr": 17, "each": [17, 19], "smoothfakedynamicallyquantizedlinear": [17, 18], "contain": [17, 18], "debug": 17, "skip_fqn_list": 18, "cur_fqn": 18, "equival": 18, "list": [18, 20], "fulli": 18, "qualifi": 18, "name": [18, 20], "skip": [18, 20], "being": 18, "process": [18, 32], "factor": 18, "custom": 19, "observ": 19, "l2": 19, "norm": [19, 20], "buffer": 19, "x_orig": 19, "sparsity_level": 20, "semi_structured_block_s": 20, "wanda": 20, "sparsifi": 20, "prune": [20, 21, 24], "propos": 20, "http": 20, "arxiv": 20, "org": 20, "ab": 20, "2306": 20, "11695": 20, "awar": 20, "method": 20, "remov": 20, "product": 20, "magnitud": 20, "three": 20, "variabl": 20, "number": 20, "spars": 20, "block": 20, "out": 20, "level": 20, "config": 20, "dict": 20, "parametr": 20, "modifi": 20, "inplac": 20, "you": [20, 32], "preserv": 20, "origin": 20, "deepcopi": 20, "squash_mask": 20, "params_to_keep": 20, "params_to_keep_per_lay": 20, "squash": 20, "mask": 20, "appropri": 20, "either": 20, "sparse_param": 20, "attach": 20, "kei": [20, 32], "save": 20, "param": 20, "specif": 20, "fqn": 20, "string": 20, "xdoctest": 20, "local": 20, "undefin": 20, "don": 20, "t": 20, "ani": 20, "hasattr": 20, "submodule1": 20, "keep": 20, "linear1": 20, "foo": 20, "bar": 20, "submodule2": 20, "linear42": 20, "baz": 20, "print": [20, 32], "42": 20, "24": 20, "some": 20, "update_mask": 20, "tensor_nam": 20, "statist": 20, "retriev": 20, "first": 20, "act_per_input": 20, "Then": 20, "metric": 20, "matrix": 20, "across": 20, "whole": 20, "simul": 21, "It": 21, "ao": 21, "open": 24, "librari": 24, "provid": 24, "nativ": 24, "our": 24, "under": 24, "develop": 24, "content": 24, "come": 24, "soon": 24, "00": [28, 31], "003": [28, 31, 32], "total": [28, 31, 32], "execut": [28, 31], "file": [28, 31], "galleri": [28, 30, 32], "mem": [28, 31], "mb": [28, 31], "templat": [28, 30, 31], "tutori": [28, 30, 31], "tutorials_sourc": 28, "template_tutori": [28, 31, 32], "py": [28, 31, 32], "download": [30, 32], "python": [30, 32], "tutorials_python": 30, "zip": 30, "jupyt": [30, 32], "notebook": [30, 32], "tutorials_jupyt": 30, "sphinx": [30, 32], "go": 32, "end": 32, "full": 32, "author": 32, "firstnam": 32, "lastnam": 32, "what": 32, "item": 32, "3": 32, "prerequisit": 32, "v2": 32, "gpu": 32, "describ": 32, "why": 32, "topic": 32, "import": 32, "add": 32, "link": 32, "research": 32, "paper": 32, "walk": 32, "through": 32, "below": 32, "automat": 32, "rand": 32, "4807": 32, "3106": 32, "7760": 32, "7089": 32, "2909": 32, "6290": 32, "6120": 32, "6692": 32, "3182": 32, "6337": 32, "6246": 32, "3624": 32, "2676": 32, "4523": 32, "0659": 32, "practic": 32, "user": 32, "test": 32, "knowledg": 32, "nlp": 32, "scratch": 32, "summar": 32, "concept": 32, "cover": 32, "highlight": 32, "takeawai": 32, "link1": 32, "link2": 32, "time": 32, "script": 32, "minut": 32, "second": 32, "ipynb": 32}, "objects": {"torchao.dtypes": [[6, 0, 1, "", "AffineQuantizedTensor"], [7, 2, 1, "", "to_affine_quantized"], [8, 2, 1, "", "to_nf4"]], "torchao.dtypes.AffineQuantizedTensor": [[6, 1, 1, "", "dequantize"], [6, 1, 1, "", "to"]], "torchao.quantization": [[9, 0, 1, "", "Int4WeightOnlyGPTQQuantizer"], [10, 0, 1, "", "Int4WeightOnlyQuantizer"], [11, 0, 1, "", "SmoothFakeDynQuantMixin"], [12, 0, 1, "", "SmoothFakeDynamicallyQuantizedLinear"], [13, 2, 1, "", "int4_weight_only"], [14, 2, 1, "", "int8_dynamic_activation_int4_weight"], [15, 2, 1, "", "int8_dynamic_activation_int8_weight"], [16, 2, 1, "", "int8_weight_only"], [17, 2, 1, "", "smooth_fq_linear_to_inference"], [18, 2, 1, "", "swap_linear_with_smooth_fq_linear"]], "torchao.quantization.SmoothFakeDynQuantMixin": [[11, 1, 1, "", "set_debug_x_absmax"]], "torchao.quantization.SmoothFakeDynamicallyQuantizedLinear": [[12, 1, 1, "", "forward"], [12, 1, 1, "", "from_float"], [12, 1, 1, "", "set_debug_x_absmax"], [12, 1, 1, "", "to_inference"]], "torchao": [[4, 3, 0, "-", "sparsity"]], "torchao.sparsity": [[19, 0, 1, "", "PerChannelNormObserver"], [20, 0, 1, "", "WandaSparsifier"], [21, 2, 1, "", "apply_fake_sparsity"], [22, 2, 1, "", "apply_sparse_semi_structured"]], "torchao.sparsity.PerChannelNormObserver": [[19, 1, 1, "", "forward"]], "torchao.sparsity.WandaSparsifier": [[20, 1, 1, "", "prepare"], [20, 1, 1, "", "squash_mask"], [20, 1, 1, "", "update_mask"]]}, "objtypes": {"0": "py:class", "1": "py:method", "2": "py:function", "3": "py:module"}, "objnames": {"0": ["py", "class", "Python class"], "1": ["py", "method", "Python method"], "2": ["py", "function", "Python function"], "3": ["py", "module", "Python module"]}, "titleterms": {"torchao": [0, 1, 2, 3, 4, 24], "dtype": [0, 5], "api": [1, 24], "refer": [1, 24], "python": 1, "kernel": [2, 26], "quantiz": [3, 27], "sparsiti": [4, 29], "affinequantizedtensor": 6, "to_affine_quant": 7, "to_nf4": 8, "int4weightonlygptqquant": 9, "int4weightonlyquant": 10, "smoothfakedynquantmixin": 11, "smoothfakedynamicallyquantizedlinear": 12, "int4_weight_onli": 13, "int8_dynamic_activation_int4_weight": 14, "int8_dynamic_activation_int8_weight": 15, "int8_weight_onli": 16, "smooth_fq_linear_to_infer": 17, "swap_linear_with_smooth_fq_linear": 18, "perchannelnormobserv": 19, "wandasparsifi": 20, "apply_fake_spars": 21, "apply_sparse_semi_structur": 22, "get": 23, "start": 23, "welcom": 24, "document": 24, "overview": [25, 32], "perform": 26, "comput": [28, 31], "time": [28, 31], "templat": 32, "tutori": 32, "step": 32, "option": 32, "addit": 32, "exercis": 32, "conclus": 32, "further": 32, "read": 32}, "envversion": {"sphinx.domains.c": 2, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 6, "sphinx.domains.index": 1, "sphinx.domains.javascript": 2, "sphinx.domains.math": 2, "sphinx.domains.python": 3, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx.ext.intersphinx": 1, "sphinx.ext.todo": 2, "sphinx.ext.viewcode": 1, "sphinx": 56}})