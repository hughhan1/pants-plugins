from typing import Final


class AriadneAddressConstants:
    """Constants for the Pants target generated from the third-party `ariadne` package."""

    TargetName: Final = "requirements"
    GeneratedName: Final = "ariadne"


GraphQLTargetSuffix: Final = ".graphql"
GraphQLTargetsGlob: Final = f"*{GraphQLTargetSuffix}"
