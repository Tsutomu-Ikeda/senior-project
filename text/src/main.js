const fs = require('fs');
require('log-timestamp');
const cheerio = require('cheerio');
const marked = require("marked");
const puppeteer = require('puppeteer-core');
const { PDFDocument } = require('pdf-lib');
const liveServer = require("live-server");

function convertToLowerRoman(num) {
  var decimal = [ 1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1 ];
  var romanNumeral = [ 'm', 'cm', 'd', 'cd', 'c', 'xc', 'l', 'xl', 'x', 'ix', 'v', 'iv', 'i' ];

  var romanized = '';

  for (var i = 0; i < decimal.length; i++) {
    while (decimal[i] <= num) {
      romanized += romanNumeral[i];
      num -= decimal[i];
    }
  }
  return romanized;
}

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
    const $ = cheerio.load(html);
    $('.toc a').each(
      (i, elem) => {
        $(elem).attr('href', `#${$(elem).text().toLowerCase().replace(" ", "-").replace(/\//ig, "")}`);
      }
    );
    fs.writeFileSync("./src/paper.html", $.html());

    const browser = await puppeteer.launch(
      {
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
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
    const pdf = await page.pdf({
      format: 'A4',
    });
    await browser.close();

    const pdfDoc = await PDFDocument.load(pdf);
    const pages = pdfDoc.getPages();

    const width = pages[0].getWidth();
    const characterSize = 14;

    for (let i = 0; i < pages.length; i++) {
      const appendixNum = 9;
      const getPageNumberText = (pageNumber) => {
        if (1 < i && i < pages.length - appendixNum) {
          return `${i - 1}`;
        }

        if (i > 32) {
          return convertToLowerRoman(i - 32);
        }

        return undefined;
      }
      const pageNumberText = getPageNumberText();

      if (pageNumberText) {
        const textWidth = 8.232 * pageNumberText.length;
        pages[i].drawText(
          pageNumberText,
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
