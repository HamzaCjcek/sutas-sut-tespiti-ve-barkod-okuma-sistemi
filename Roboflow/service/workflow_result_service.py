class WorkflowResultService:

    def get_result(self, result):

        if not result:
            raise RuntimeError(
                "Roboflow sonuç döndürmedi."
            )

        if isinstance(result, list):

            if len(result) == 0:
                raise RuntimeError(
                    "Roboflow boş liste döndürdü."
                )

            return result[0]

        return result