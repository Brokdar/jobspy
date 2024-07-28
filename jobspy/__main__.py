from jobspy.services.gitlab import GitlabClient
from jobspy.tui.app import JobSpy


def main() -> None:
    """Main function of the JobSpy application."""
    client = GitlabClient()
    app = JobSpy(client)
    app.run()


if __name__ == "__main__":
    main()
