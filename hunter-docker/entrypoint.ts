// hunter-docker/entrypoint.ts

import puppeteer from "puppeteer";
import { SQSClient, SendMessageCommand } from "@aws-sdk/client-sqs";

const queueUrl = process.env.QUEUE_URL;
const searchQuery =
  process.env.SEARCH_QUERY || "site:linkedin.com developer jobs";
const pageLimit = parseInt(process.env.GOOGLE_PAGE_LIMIT || "3");

const sqs = new SQSClient({ region: "us-east-1" }); // 🔁 Replace if using another region

async function scrapeAndSendToQueue() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();

  for (let i = 0; i < pageLimit; i++) {
    const start = i * 10;
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(
      searchQuery
    )}&start=${start}`;
    await page.goto(searchUrl, { waitUntil: "domcontentloaded" });

    const links = await page.$$eval("a", (anchors) =>
      anchors
        .map((a) => a.href)
        .filter(
          (href) =>
            href.includes("linkedin.com") && !href.includes("google.com")
        )
    );

    for (const link of links) {
      const command = new SendMessageCommand({
        QueueUrl: queueUrl,
        MessageBody: link,
      });

      try {
        await sqs.send(command);
        console.log(`✅ Sent to SQS: ${link}`);
      } catch (error) {
        console.error(`❌ Failed to send to SQS: ${link}`, error);
      }
    }
  }

  await browser.close();
}

scrapeAndSendToQueue().catch((err) => {
  console.error("Unhandled error:", err);
  process.exit(1);
});
