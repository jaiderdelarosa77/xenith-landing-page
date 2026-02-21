import ReactPDF from '@react-pdf/renderer'
import { QuotationPDFDocument } from './templates/quotation'
import { Quotation } from '@/lib/validations/quotation'

export async function generateQuotationPDF(quotation: Quotation): Promise<Buffer> {
  const doc = QuotationPDFDocument({ quotation })
  const pdfStream = await ReactPDF.renderToStream(doc)

  // Convert stream to buffer
  const chunks: Buffer[] = []

  return new Promise((resolve, reject) => {
    pdfStream.on('data', (chunk: Buffer) => chunks.push(chunk))
    pdfStream.on('end', () => resolve(Buffer.concat(chunks)))
    pdfStream.on('error', reject)
  })
}
