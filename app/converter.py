import markdown
from weasyprint import HTML, CSS

def generate_pdf_from_markdown(md_content, output_path):
    html_fragment = markdown.markdown(
        md_content,
        extensions=[
            'fenced_code',
            'tables',
            'codehilite',
            'nl2br',
            'sane_lists'
        ]
    )

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Converted Document</title>
    </head>
    <body>
        {html_fragment}
    </body>
    </html>
    """

    css = CSS(filename='styles.css')
    HTML(string=full_html).write_pdf(output_path, stylesheets=[css])
