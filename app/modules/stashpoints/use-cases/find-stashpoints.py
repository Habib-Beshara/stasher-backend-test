class FindStashpoints:
    def __init__(
        self,
        stashpoint_repository: StashpointRepository,
        data: IFindStashpointsInput,
    ):
        self.data = data
        self.stashpoint_repository = stashpoint_repository
        self.validation_service = validation_service
        self.response = Response()

    def exec(self) -> Response:
        valid = self.validate_input()
        if valid:
            try:
                # Core use case logic goes here
                stashpoints = self.stashpoint_repository.find(self.data)
                self.response.set_payload(stashpoints)
            except Exception as error:
                print(error)
                self.response.add_errors([error])
        return self.response

    def validate_input(self) -> bool:
        validate = self.validation_service.compile(find_stashpoints_input_schema)
        valid = validate(self.data)
        if not valid:
            # Assume validate.errors is a list of error messages
            errors = [Exception(error) for error in getattr(validate, 'errors', [])]
            self.response.add_errors(errors)
        return valid
