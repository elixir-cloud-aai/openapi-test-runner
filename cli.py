from job_runner import JobRunner
import click

@click.group()
def main():
    pass


@main.command(help='Run TES compliance tests against the servers')
@click.option('--tag', '-t', multiple=True, help='Tag')
def report(tag):

    if len(tag) == 0:
        tag = "All",
    print(f"Input tag is - {tag}")
    job_runner = JobRunner(tag)
    job_runner.run_jobs()


if __name__ == "__main__":
    main()