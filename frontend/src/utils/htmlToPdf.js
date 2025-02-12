import { jsPDF } from "jspdf"

export const exportHtmlToPdf = async (
  id,
  name,
  header = "",
  usingId = true,
  orientation = "l",
  size = "a1"
) => {
  return new Promise((resolve, reject) => {
    var pdf = new jsPDF(orientation, "px", size)
    let source = usingId ? document.getElementById(id) : id
    let margins = {
      top: 40,
      bottom: 35,
      left: 10,
      right: 10
    }
    pdf.setFont("helvetica")
    pdf.html(
      source,
      {
        x: margins.left,
        y: margins.top,
        callback: async function (dispose) {
          pdf.setFontSize(35)
          pdf.setPage(1)
          const pageSize = pdf.internal.pageSize
          const pageWidth = pageSize.width || pageSize.getWidth()
          const pageHeight = pageSize.height || pageSize.getHeight()
          const pageCount = pdf.internal.getNumberOfPages()
          // Header
          pdf.text(header, pageWidth / 2 - pdf.getTextWidth(header) / 2, 10, {
            baseline: "top"
          })
          pdf.setPage(pageCount)
          const footer = name.substring(0, name.length - 4)
          pdf.setFontSize(30)
          pdf.text(
            footer,
            pageWidth / 2 - pdf.getTextWidth(footer) / 2,
            pageHeight - 15,
            { baseline: "bottom" }
          )
          await pdf
            .save(name, {
              returnPromise: true
            })
            .then((e) => {
              resolve("done")
            })
            .catch((e) => {
              reject(e)
            })
        }
      },
      margins
    )
  })
}

export const exportTextToPdf = async (
  text,
  name,
  orientation = "l",
  size = "a1"
) => {
  return new Promise((resolve, reject) => {
    var pdf = new jsPDF(orientation, "px", size)
    pdf.setFont("helvetica")
    pdf.setFontSize(9)
    pdf.text(text)
    pdf
      .save(name, {
        returnPromise: true
      })
      .then((e) => {
        resolve("done")
      })
      .catch((e) => {
        reject(e)
      })
  })
}
