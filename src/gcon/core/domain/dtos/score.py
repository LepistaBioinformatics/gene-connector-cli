from attrs import field, frozen


@frozen(kw_only=True)
class ConnectionScores:
    """Connection scores class.

    Attributes:
        observed_completeness_score (int): The observed completeness score.
        reachable_completeness_score (int): The reachable completeness score.

    Methods:
        to_dict: Convert the connection scores to a dictionary.

    """

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    observed_completeness_score: float = field()
    reachable_completeness_score: float = field()

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def to_dict(self) -> dict[str, float]:
        """Convert the connection scores to a dictionary.

        Returns:
            dict[str, int]: The connection scores as a dictionary.

        """

        return {
            "observed_completeness_score": self.observed_completeness_score,
            "reachable_completeness_score": self.reachable_completeness_score,
        }
