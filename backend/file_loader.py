import os

from PyPDF2 import PdfReader
from docx import Document


# ==================================================
# READ FILE
# ==================================================

def read_file(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()


    # ==================================================
    # TXT
    # ==================================================

    if extension == ".txt":

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        return clean_text(text)


    # ==================================================
    # PDF
    # ==================================================

    elif extension == ".pdf":

        reader = PdfReader(
            file_path
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            try:

                page_text = page.extract_text()

                if page_text:

                    pages.append(
                        f"\n[Page {page_number}]\n"
                        f"{page_text}"
                    )

            except Exception as error:

                print(
                    f"Could not read PDF page "
                    f"{page_number}: {error}"
                )

        text = "\n".join(pages)

        return clean_text(text)


    # ==================================================
    # DOCX
    # ==================================================

    elif extension == ".docx":

        document = Document(
            file_path
        )

        parts = []

        # Paragraphs
        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                parts.append(
                    paragraph.text
                )

        # Tables
        for table in document.tables:

            for row in table.rows:

                row_text = []

                for cell in row.cells:

                    if cell.text.strip():

                        row_text.append(
                            cell.text.strip()
                        )

                if row_text:

                    parts.append(
                        " | ".join(row_text)
                    )

        text = "\n".join(parts)

        return clean_text(text)


    # ==================================================
    # UNSUPPORTED
    # ==================================================

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )


# ==================================================
# CLEAN TEXT
# ==================================================

def clean_text(text):

    if not text:
        return ""

    # Remove null characters
    text = text.replace(
        "\x00",
        ""
    )

    # Normalize line endings
    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    # Remove excessive spaces
    lines = []

    for line in text.split("\n"):

        cleaned = " ".join(
            line.split()
        )

        if cleaned:

            lines.append(
                cleaned
            )

    return "\n".join(lines).strip()