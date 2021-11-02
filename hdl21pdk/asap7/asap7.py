""" 

# Hdl21 + ASAP7 PDK Modules and Transformations 

Defines a set of `hdl21.ExternalModule`s comprising the essential devices of the ASAP7 predictive-technology PDK, 
defined at https://github.com/The-OpenROAD-Project/asap7, 
and an `hdl21pdk.netlist` method for converting process-portable `hdl21.Primitive` elements into these modules. 

FIXME!: The primitive components of the ASAP7 PDK are comprised solely of core Mos transistors `{n,p}mos_{rvt,lvt,slvt,sram}`. 
Unlike the common subckt-based models provided by physical PDKs, the ASAP7 transistors are provided solely 
as BSIM-CMG `.model` definitions. 

"""

import copy
from typing import Union
from types import SimpleNamespace
from dataclasses import asdict

import hdl21 as h
from hdl21.primitives import Mos, MosType, MosVth, MosParams


# Collected `ExternalModule`s are stored in the `modules` namespace
modules = SimpleNamespace()

_mos_typenames = {
    MosType.NMOS: "n",
    MosType.PMOS: "p",
}
_mos_vtnames = {
    MosVth.STD: "_rvt",
    MosVth.LOW: "_lvt",
    "SLVT": "_slvt",
    "SRAM": "_sram",
}
# Create a lookup table from `MosParams` attributes to `ExternalModule`s
_mos_modules = dict()  # `Dict[(MosType, MosVth), ExternalModule]`, if that worked

# Create each Mos `ExternalModule`
for tp, tpname in _mos_typenames.items():
    for vt, vtname in _mos_vtnames.items():

        modname = f"{tp}mos{vtname}"
        mod = h.ExternalModule(
            domain="asap7",
            name=modname,
            desc=f"ASAP7 PDK Mos {modname}",
            port_list=copy.deepcopy(Mos.port_list),
            paramtype=object,
        )

        # Add it to the `params => ExternalModules` lookup table
        _mos_modules[(tp, vt)] = mod

        # And add it, with its module-name as key, to the modules namespace
        setattr(modules, modname, mod)


class Asap7Walker(h.HierarchyWalker):
    """ Hierarchical Walker, converting `h.Primitive` instances to process-defined `ExternalModule`s. """

    def __init__(self):
        self.mos_modcalls = dict()

    def visit_instance(self, inst: h.Instance):
        """ Replace instances of `h.Primitive` with our `ExternalModule`s """
        if isinstance(inst.of, h.PrimitiveCall):
            inst.of = self.replace_primitive(inst.of)
            return
        # Otherwise keep traversing, instance unmodified
        return super().visit_instance(inst)

    def replace_primitive(
        self, primcall: h.PrimitiveCall
    ) -> Union[h.ExternalModuleCall, h.PrimitiveCall]:
        # Replace transistors
        if primcall.prim is h.primitives.Mos:
            return self.mos_module_call(primcall.params)
        # Return everything else as-is
        return primcall

    def mos_module(self, params: MosParams) -> h.ExternalModule:
        """ Retrieve or create an `ExternalModule` for a MOS of parameters `params`. """
        mod = _mos_modules.get((params.tp, params.vth), None)
        if mod is None:
            raise RuntimeError(f"No Mos module {modname}")
        return mod

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """ Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in self.mos_modcalls:
            return self.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)

        # Translate its parameters
        # FIXME: further parameter transformations likely to come
        modparams = asdict(params)
        modparams.pop("vth", None)

        # Combine the two into a call, cache and return it
        modcall = mod(modparams)
        self.mos_modcalls[params] = modcall
        return modcall


def compile(src: h.proto.Package) -> h.proto.Package:
    """ Compile proto-Package `src` to the ASAP7 technology """
    ns = h.from_proto(src)
    Asap7Walker().visit_namespace(ns)
    return h.to_proto(ns)