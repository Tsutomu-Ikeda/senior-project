const fs = require('fs');
require('log-timestamp');
const marked = require("marked");
const puppeteer = require('puppeteer');
const { PDFDocument } = require('pdf-lib');
const liveServer = require("live-server");

const config = {
  liveServerPort: 5555,
};

var params = {
  port: config.liveServerPort,
  host: "0.0.0.0",
  root: "./src",
  open: false,
  logLevel: 2,
  ignore: [
    '**/*.md'
  ]
};

const srcFolder = './src/';
const renderer = new marked.Renderer;
renderer.paragraph = function (text) {
  if (text.startsWith('<figure') && text.endsWith('</figure>'))
    return text;
  if (text.startsWith('<img') && text.endsWith('>'))
    return text;
  else
    return '<p>' + text + '</p>';
}
marked.setOptions({
  renderer
});

console.log(`Watching for file changes on ${srcFolder}`);

let isProcessing = false;

fs.watch(srcFolder, async (event, filename) => {
  if (isProcessing) return;
  isProcessing = true;
  console.log(filename);
  if (!filename.match(/\.md$/) && !filename.match(/\.css$/)) {
    isProcessing = false;
    return;
  }

  try {
    file = fs.readFileSync(`${srcFolder}paper.md`, { encoding: "utf8" });

    const html = marked(`${file}\n<script>
    document.addEventListener('DOMContentLoaded', (event) => {
      document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
      });
    });
    </script></body>\n`);
    fs.writeFileSync("./src/paper.html", html);

    const browser = await puppeteer.launch(
      {
        args: ["--no-sandbox", "--disable-setuid-sandbox"]
      }
    );
    const page = await browser.newPage();
    await page.goto(
      `http://localhost:${config.liveServerPort}/paper.html`,
      { waitUntil: 'networkidle2' }
    );
    await page.waitForSelector('span.mjx-mn');
    const title = await page.title();
    const pdf = await page.pdf();
    await browser.close();

    const pdfDoc = await PDFDocument.load(pdf);
    const pages = pdfDoc.getPages();

    const width = pages[0].getWidth();
    const characterSize = 14;

    for (let i = 0; i < pages.length; i++) {
      const pageNumber = i - 1;
      if (pageNumber > 0 && i < pages.length - 1) {
        const textWidth = 8.232 * pageNumber.toString().length;
        pages[i].drawText(
          `${pageNumber}`,
          {
            x: (width - textWidth) / 2,
            y: 40,
            size: characterSize,
          }
        )
      }
    }
    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync(
      `${title}.pdf`,
      pdfBytes
    );
    console.log(title);
  }
  catch (err) {
    if (err) {
      console.error(err.message);
    }
  };
  isProcessing = false;
});

liveServer.start(params);
