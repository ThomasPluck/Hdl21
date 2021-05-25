"""
# Hdl21 Primitive Modules

Primitives are leaf-level Modules typically defined not by users, 
but by simulation tools or device fabricators. 
Prominent examples include MOS transistors, diodes, resistors, and capacitors. 

"""

from pydantic.dataclasses import dataclass
from dataclasses import replace
from enum import Enum
from typing import Optional, Any, List, Type

# Local imports
from .params import paramclass, Param, isparamclass
from .signal import Port, Signal, Visibility
from .instance import calls_instantiate


@dataclass
class Primitive:
    """ # hdl21 Primitive Component 
    
    Primitives are leaf-level Modules typically defined not by users, 
    but by simulation tools or device fabricators. 
    Prominent examples include MOS transistors, diodes, resistors, and capacitors. 
    """

    name: str
    desc: str
    port_list: List[Signal]
    paramtype: Type

    def __post_init_post_parse__(self):
        """ After type-checking, do plenty more checks on values """
        if not isparamclass(self.paramtype):
            raise TypeError(
                f"Invalid Primitive param-type {self.paramtype} for {self.name}, must be an `hdl21.paramclass`"
            )
        for p in self.port_list:
            if not p.name:
                raise ValueError(f"Unnamed Primitive Port {p} for {self.name}")
            if p.vis != Visibility.PORT:
                raise ValueError(
                    f"Invalid Primitive Port {p.name} on {self.name}; must have PORT visibility"
                )

    def __call__(self, params: Any) -> "PrimitiveCall":
        return PrimitiveCall(prim=self, params=params)

    @property
    def Params(self) -> Type:
        return self.paramtype

    @property
    def ports(self) -> dict:
        return {p.name: p for p in self.port_list}


@calls_instantiate
@dataclass
class PrimitiveCall:
    """ Primitive Call
    A combination of a Primitive and its Parameter-values, 
    typically generated by calling the Primitive. """

    prim: Primitive
    params: Any

    def __post_init_post_parse__(self):
        # Type-validate our parameters
        if not isinstance(self.params, self.prim.paramtype):
            raise TypeError(
                f"Invalid parameters {self.params} for Primitive {self.prim}. Must be {self.prim.paramtype}"
            )

    @property
    def ports(self) -> dict:
        return self.prim.ports


class MosType(Enum):
    """ NMOS/PMOS Type Enumeration """

    NMOS = 0
    PMOS = 1


class MosVth(Enum):
    """ MOS Threshold Enumeration """

    STD = 2
    # Moar coming soon!


@paramclass
class MosParams:
    """ MOS Transistor Parameters """

    w = Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = Param(dtype=Optional[int], desc="Length in resolution units", default=None)
    nser = Param(dtype=int, desc="Number of series fingers", default=1)
    npar = Param(dtype=int, desc="Number of parallel fingers", default=1)
    tp = Param(dtype=MosType, desc="MosType (PMOS/NMOS)", default=MosType.NMOS)
    vth = Param(dtype=MosVth, desc="Threshold voltage specifier", default=MosVth.STD)

    def __post_init_post_parse__(self):
        """ Value Checks """
        if self.w <= 0:
            raise ValueError(f"MosParams with invalid width {self.w}")
        if self.l <= 0:
            raise ValueError(f"MosParams with invalid length {self.l}")
        if self.npar <= 0:
            raise ValueError(
                f"MosParams with invalid number parallel fingers {self.npar}"
            )
        if self.nser <= 0:
            raise ValueError(
                f"MosParams with invalid number series fingers {self.nser}"
            )


Mos = Primitive(
    name="Mos",
    desc="Mos Transistor",
    port_list=[Port(name="d"), Port(name="g"), Port(name="s"), Port(name="b")],
    paramtype=MosParams,
)


def Nmos(params: MosParams) -> Primitive:
    """ Nmos Constructor. A thin wrapper around `hdl21.primitives.Mos` """
    return Mos(replace(params, tp=MosType.NMOS))


def Pmos(params: MosParams) -> Primitive:
    """ Pmos Constructor. A thin wrapper around `hdl21.primitives.Mos` """
    return Mos(replace(params, tp=MosType.PMOS))


@paramclass
class DiodeParams:
    w = Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = Param(dtype=Optional[int], desc="Length in resolution units", default=None)

    # FIXME: will likely want a similar type-switch, at least eventually
    # tp = Param(dtype=Tbd!, desc="Diode type specifier")


Diode = Primitive(
    name="Diode",
    desc="Diode",
    port_list=[Port(name="p"), Port(name="n")],
    paramtype=DiodeParams,
)


# Common alias(es)
D = Diode


@paramclass
class ResistorParams:
    r = Param(dtype=float, desc="Resistance (ohms)")


Resistor = Primitive(
    name="Resistor",
    desc="Resistor",
    port_list=[Port(name="p"), Port(name="n")],
    paramtype=ResistorParams,
)


# Common aliases
R = Res = Resistor


@paramclass
class CapacitorParams:
    c = Param(dtype=float, desc="Capacitance (F)")


Capacitor = Primitive(
    name="Capacitor",
    desc="Capacitor",
    port_list=[Port(name="p"), Port(name="n")],
    paramtype=CapacitorParams,
)


# Common aliases
C = Cap = Capacitor


@paramclass
class InductorParams:
    l = Param(dtype=float, desc="Inductance (H)")


Inductor = Primitive(
    name="Inductor",
    desc="Inductor",
    port_list=[Port(name="p"), Port(name="n")],
    paramtype=InductorParams,
)


# Common alias(es)
L = Inductor


@paramclass
class ShortParams:
    layer = Param(dtype=Optional[int], desc="Metal layer", default=None)
    w = Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = Param(dtype=Optional[int], desc="Length in resolution units", default=None)


Short = Primitive(
    name="Short",
    desc="Short-Circuit/ Net-Tie",
    port_list=[Port(name="p"), Port(name="n")],
    paramtype=ShortParams,
)
