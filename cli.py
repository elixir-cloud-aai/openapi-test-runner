from job_runner import JobRunner
import click

@click.group()
def main():
    pass

@main.command(help='Run TES compliance tests against the servers')
@click.option('--tag', '-t', multiple=True, help='Tag')
def report(tag):
    # print(tag)
    job_runner = JobRunner(tag)
    job_runner.run_jobs()

if __name__ == "__main__":
    main()