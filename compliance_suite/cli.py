import click
from endpoints import service_info, list_tasks, create_task, get_task, cancel_task


@click.group()
def main():
    pass


@main.command(help='Run TES compliance tests against the servers')
@click.option('--server', '-s', multiple=True, help='server_url')
def report(server):

    if len(server) == 0:
        raise Exception('No server url provided. Provide at least one')

    for s in server:
        print(f"Start validation for {s} ")

        service_info.get_service_info(s)
        # list_tasks.list_tasks_minimal(s)
        # list_tasks.list_tasks_basic(s)
        # list_tasks.list_tasks_full(s)
        # create_task.create_task(s)
        # get_task.get_tasks_minimal(s)
        # get_task.get_tasks_basic(s)
        # get_task.get_tasks_full(s)
        # cancel_task.cancel_task(s)


if __name__ == "__main__":
    main()