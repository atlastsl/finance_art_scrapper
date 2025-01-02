import pdfkit


if __name__ == "__main__":
    def html_to_pdf(url, output_pdf):
        # Convertir HTML en PDF
        wkhtml_path = pdfkit.configuration(
            wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
        )  # by using configuration you can add path value.
        pdfkit.from_string(url, output_pdf, configuration=wkhtml_path)
        print(f"L'article de {url} a été converti avec succès en {output_pdf}.")


    html_to_pdf(
        "https://lautorite.qc.cahttps://lautorite.qc.ca/grand-public/salle-de-presse/actualites/fiche-dactualite"
        "/tanya-sirois-nommee-au-conseil-dadministration-de-lautorite",
        "C:/Users/AYSIF/PycharmProjects/TwikitTest/src/test.pdf"
    )
