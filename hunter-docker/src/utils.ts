import fs from "fs-extra";
import path from "path";

export const sleep = (ms: number) => new Promise((res) => setTimeout(res, ms));

export function sessionDir(): string {
  const dir = path.join(process.cwd(), "sessions");
  fs.ensureDirSync(dir);
  return dir;
}

export function randomFromArray<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}
