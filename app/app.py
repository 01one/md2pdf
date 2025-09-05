import os
import asyncio
import tempfile
import uuid
import tornado.web
import tornado.log
from datetime import datetime

import converter


MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("template.html",xsrf_token=self.xsrf_token)

class UploadHandler(tornado.web.RequestHandler):
    async def post(self):
        if 'mdfile' not in self.request.files:
            self.set_status(400)
            self.write("No file uploaded. Please select a .md file to convert.")
            return
            
        file_info = self.request.files['mdfile'][0]
        file_body = file_info['body']

        if len(file_body) > MAX_FILE_SIZE:
            self.set_status(413) # Payload Too Large
            self.write(f"File size exceeds the limit of {MAX_FILE_SIZE / 1024 / 1024:.0f}MB.")
            return

        try:
            md_content = file_body.decode('utf-8')
        except UnicodeDecodeError:
            self.set_status(400)
            self.write("Invalid file encoding. Please ensure the file is UTF-8 encoded.")
            return


        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, f"output-{uuid.uuid4()}.pdf")
            
            try:
                await asyncio.to_thread(
                    converter.generate_pdf_from_markdown, 
                    md_content, 
                    pdf_path
                )
            except Exception as e:
                tornado.log.app_log.error(f"PDF conversion failed: {e}")
                self.set_status(500)
                self.write("An error occurred during PDF conversion. Please check the Markdown file for issues.")
                return


            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            download_filename = f"markdown_to_pdf_document_{timestamp}.pdf"

            self.set_header('Content-Type', 'application/pdf')
            self.set_header('Content-Disposition', f'attachment; filename="{download_filename}"')
            
            with open(pdf_path, 'rb') as f:
                self.write(f.read())

def make_app():
    tornado.log.enable_pretty_logging()
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "xsrf_cookies": True,
        "debug": True
    }
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/upload", UploadHandler),
    ], **settings)



async def main():
    app = make_app()
    app.listen(5000)
    print("Server started on http://localhost:5000")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutting down.")
