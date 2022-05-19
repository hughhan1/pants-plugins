from typing import Iterable

from pants.backend.python.dependency_inference.rules import InferPythonImportDependencies, PythonInferSubsystem
from pants.backend.python.target_types import PythonSourceField
from pants.core.target_types import AllAssetTargets, AllAssetTargetsRequest, ResourceSourceField
from pants.engine.rules import Get, Rule, rule
from pants.engine.target import InferDependenciesRequest, InferredDependencies
from pants.engine.unions import UnionRule

from ariadne.constants import AriadneAddressConstants, GraphQLTargetSuffix


class InferPythonGraphQLResourceDependenciesRequest(InferDependenciesRequest):
    infer_from = PythonSourceField  # noqa


@rule(desc="Inferring Python GraphQL dependencies by analyzing source")
async def infer_python_graphql_dependencies(
    request: InferPythonGraphQLResourceDependenciesRequest, python_infer_subsystem: PythonInferSubsystem
) -> InferredDependencies:
    if not python_infer_subsystem.imports and not python_infer_subsystem.assets:
        return InferredDependencies([])

    inferred_dependencies = await Get(InferredDependencies, InferPythonImportDependencies(request.sources_field))

    has_graphql_dependency = False
    for dependency in inferred_dependencies.dependencies:
        if (
            dependency.target_name == AriadneAddressConstants.TargetName
            and dependency.generated_name == AriadneAddressConstants.GeneratedName
        ):
            has_graphql_dependency = True
            break

    if not has_graphql_dependency:
        return InferredDependencies([])

    graphql_targets = set()
    all_asset_targets = await Get(AllAssetTargets, AllAssetTargetsRequest())

    # We only care about resources because we declare GraphQL targets as resources.
    for target in all_asset_targets.resources:
        if target.field_values[ResourceSourceField].value.endswith(GraphQLTargetSuffix):
            graphql_targets.add(target)

    if len(graphql_targets) == 0:
        return InferredDependencies([])

    return InferredDependencies(target.address for target in graphql_targets)


def rules() -> Iterable[Rule]:
    return [
        infer_python_graphql_dependencies,
        UnionRule(InferDependenciesRequest, InferPythonGraphQLResourceDependenciesRequest),
    ]
