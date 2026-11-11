// Piyasa Masası okuyucu sayacı
// Her tarayıcı rastgele bir kimlik üretir; her gün (Türkiye saati) her kimlik için tek bir kayıt açılır.
// Sayım = o günün kayıt sayısı (tekil günlük okuyucu). Okuma-değiştirme-yazma sayacı yok; her ziyaretçi yeni bir anahtar.
import { getStore } from "@netlify/blobs";

const gunTR = (d = new Date()) =>
  new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Istanbul" }).format(d); // YYYY-MM-DD

const BOT = /bot|crawl|spider|slurp|preview|facebookexternalhit|whatsapp|telegram|headless/i;

async function say(store, gun) {
  const { blobs } = await store.list({ prefix: `gun/${gun}/` });
  return blobs.length;
}

export default async (req) => {
  const store = getStore({ name: "ziyaretler", consistency: "strong" });
  const url = new URL(req.url);

  if (req.method === "POST") {
    const gun = gunTR();
    const ua = req.headers.get("user-agent") || "";
    let id = "";
    try { id = String((await req.json()).id || ""); } catch {}
    if (!BOT.test(ua) && /^[A-Za-z0-9-]{8,64}$/.test(id)) {
      await store.set(`gun/${gun}/${id}`, "1", { onlyIfNew: true });
    }
    return Response.json({ gun, bugun: await say(store, gun) }, { headers: { "cache-control": "no-store" } });
  }

  const n = Math.min(60, Math.max(1, parseInt(url.searchParams.get("gunler") || "1", 10) || 1));
  const gunler = [];
  for (let i = 0; i < n; i++) {
    const g = gunTR(new Date(Date.now() - i * 86400000));
    gunler.push({ gun: g, okuyucu: await say(store, g) });
  }
  return Response.json({ gunler }, { headers: { "cache-control": "public, max-age=60" } });
};

export const config = { path: "/api/ziyaret" };
