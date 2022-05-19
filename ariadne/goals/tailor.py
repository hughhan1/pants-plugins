from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from pants.core.goals.tailor import (
    AllOwnedSources,
    PutativeTarget,
    PutativeTargets,
    PutativeTargetsRequest,
    group_by_dir,
)
from pants.core.target_types import ResourcesGeneratorTarget
from pants.engine.fs import PathGlobs, Paths
from pants.engine.internals.selectors import Get
from pants.engine.rules import Rule, rule
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel

from ariadne.constants import GraphQLTargetsGlob


@dataclass(frozen=True)
class PutativeGraphQLTargetsRequest(PutativeTargetsRequest):
    pass


@rule(level=LogLevel.DEBUG, desc="Determine candidate GraphQL targets to create")
async def find_putative_targets(
    req: PutativeGraphQLTargetsRequest, all_owned_sources: AllOwnedSources
) -> PutativeTargets:
    all_graphql_files = await Get(Paths, PathGlobs, req.search_paths.path_globs(GraphQLTargetsGlob))
    unowned_graphql_files = set(all_graphql_files.files) - set(all_owned_sources)
    return PutativeTargets(
        [
            # TODO(PLATS-509): invoke `PutativeTarget.for_target_type(ResourcesGeneratorTarget, ...)` instead once
            #                  https://github.com/pantsbuild/pants/issues/15527 is resolved.
            PutativeTarget(
                path=dirname,
                name="graphql_schema",
                type_alias=ResourcesGeneratorTarget.alias,
                owned_sources=(GraphQLTargetsGlob,),
                triggering_sources=sorted(filenames),
                addressable=True,
                kwargs={"sources": (GraphQLTargetsGlob,)},
            )
            for dirname, filenames in group_by_dir(unowned_graphql_files).items()
        ]
    )


def rules() -> Iterable[Rule]:
    return [find_putative_targets, UnionRule(PutativeTargetsRequest, PutativeGraphQLTargetsRequest)]
