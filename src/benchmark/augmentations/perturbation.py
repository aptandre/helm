from abc import ABC, abstractmethod
from dataclasses import replace
from random import Random
from typing import Any, Dict, Sequence, Optional


from .perturbation_description import PerturbationDescription
from benchmark.scenarios.scenario import Instance, Reference
from common.object_spec import ObjectSpec, create_object


class Perturbation(ABC):

    # Unique name to describe perturbation
    name: str

    # Whether to perturb references
    should_perturb_references: bool = False

    # Random seed
    seed: Optional[int] = None

    @property
    def description(self) -> PerturbationDescription:
        """Description of the perturbation."""
        return PerturbationDescription(name=self.name)

    def get_instance_variables(self) -> Dict[str, Any]:
        return {}

    def apply(self, instance: Instance) -> Instance:
        """
        Generates a new Instance by perturbing the input, tagging the Instance and perturbing the References,
        if should_perturb_references is true. Initializes a random number generator based on instance_id that gets
        passed to perturb and perturb_references.
        """
        assert instance.id is not None
        # If seed exists, use it as part of the random seed
        rng: Random = Random(instance.id if self.seed is None else str(self.seed) + instance.id)

        kwargs = self.get_instance_variables()
        references: Sequence[Reference] = instance.references
        if self.should_perturb_references:
            references = [self.perturb_reference(reference, rng, **kwargs) for reference in references]

        # Don't modify `id` of `Instance` here.
        # All the perturbed Instances generated from a single Instance should have the same ID.
        return replace(
            instance,
            input=self.perturb(instance.input, rng, **kwargs),
            references=references,
            perturbation=self.description,
        )

    def perturb_reference(self, reference: Reference, rng: Random, **kwargs) -> Reference:
        """Generates a new Reference by perturbing the output and tagging the Reference."""
        return replace(reference, output=self.perturb(reference.output, rng, **kwargs), tags=reference.tags)

    @abstractmethod
    def perturb(self, text: str, rng: Random, **kwargs) -> str:
        """How to perturb the text. """
        pass


class PerturbationSpec(ObjectSpec):
    """Defines how to instantiate Perturbation."""

    pass


def create_perturbation(perturbation_spec: PerturbationSpec) -> Perturbation:
    """Creates Perturbation from PerturbationSpec."""
    return create_object(perturbation_spec)
