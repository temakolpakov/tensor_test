from parser import Parser
import settings
import click


@click.command()
@click.argument('url')
def main(url):
    parser_obj = Parser(url)
    parser_obj.get_formatted_text(settings.splitter, settings.re_url)
    print(parser_obj.save_to_file(settings.base_dir))


if __name__ == '__main__':
    main()