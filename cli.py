from job_runner import JobRunner
import click

@click.group()
def main():
    pass

@main.command(help='Run TES compliance tests against the servers')
@click.option('--tags', '-t', multiple=True, help='Tags')
def report(tags):
    print(tags)
    job_runner = JobRunner(tags)
    job_runner.run_jobs()

if __name__ == "__main__":
    main()