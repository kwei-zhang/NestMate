import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useEditListing, useListing, useUploadImage } from "../api/hooks";
import { AREAS, OTHER_AREA } from "../constants";
import { useAuth } from "../store/auth";

export default function EditPost() {
  const { id } = useParams();
  const listingId = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data, isLoading } = useListing(listingId);
  const edit = useEditListing(listingId);
  const uploadImage = useUploadImage();

  const [ready, setReady] = useState(false);
  const [otherArea, setOtherArea] = useState(false);
  const [images, setImages] = useState<string[]>([]);
  const [form, setForm] = useState({
    title: "",
    has_room: false,
    area: "",
    budget_min: "",
    budget_max: "",
    has_pets: false,
    contact_type: "wechat",
    contact_value: "",
    raw_text: "",
    highlights: "",
  });

  // Prefill once the listing loads.
  useEffect(() => {
    if (!data || ready) return;
    setForm({
      title: data.title ?? "",
      has_room: data.has_room === true,
      area: data.area ?? "",
      budget_min: data.budget_min?.toString() ?? "",
      budget_max: data.budget_max?.toString() ?? "",
      has_pets: data.has_pets === true,
      contact_type: data.contact_type ?? "wechat",
      contact_value: "",
      raw_text: data.raw_text ?? "",
      highlights: (data.highlights ?? []).join("\n"),
    });
    setImages(data.images ?? []);
    setOtherArea(!!data.area && !AREAS.includes(data.area));
    setReady(true);
  }, [data, ready]);

  function set<K extends keyof typeof form>(key: K, v: (typeof form)[K]) {
    setForm({ ...form, [key]: v });
  }

  async function onFiles(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    e.target.value = "";
    for (const file of files) {
      try {
        const url = await uploadImage.mutateAsync(file);
        setImages((prev) => [...prev, url]);
      } catch {
        // skip failed uploads
      }
    }
  }

  if (isLoading || !data) return <p className="text-gray-400 text-center py-8">加载中…</p>;
  if (data.created_by !== user?.id)
    return <p className="text-red-500 text-center py-8">只能编辑自己的帖子</p>;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const highlights = form.highlights
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    await edit.mutateAsync({
      title: form.title || null,
      has_room: form.has_room,
      area: form.area || null,
      budget_min: form.budget_min ? Number(form.budget_min) : null,
      budget_max: form.budget_max ? Number(form.budget_max) : null,
      has_pets: form.has_pets,
      // Only overwrite contact when the author typed a new value.
      ...(form.contact_value
        ? { contact_type: form.contact_type, contact_value: form.contact_value }
        : {}),
      raw_text: form.raw_text,
      highlights,
      images,
    });
    navigate(`/listing/${listingId}`);
  }

  const input = "border rounded px-3 py-2 text-sm w-full";

  return (
    <form onSubmit={submit} className="max-w-xl mx-auto bg-white border rounded-lg p-6 space-y-3">
      <h1 className="text-lg font-semibold">编辑帖子</h1>

      <input
        className={input}
        placeholder="标题"
        value={form.title}
        onChange={(e) => set("title", e.target.value)}
      />
      <div className="flex gap-2">
        <select
          className={input}
          value={form.has_room ? "yes" : "no"}
          onChange={(e) => set("has_room", e.target.value === "yes")}
        >
          <option value="no">我在找房源 / 室友</option>
          <option value="yes">我有房源，找室友</option>
        </select>
        <select
          className={input}
          value={otherArea ? OTHER_AREA : form.area}
          onChange={(e) => {
            if (e.target.value === OTHER_AREA) {
              setOtherArea(true);
              set("area", "");
            } else {
              setOtherArea(false);
              set("area", e.target.value);
            }
          }}
        >
          <option value="">选择地区</option>
          {AREAS.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
          <option value={OTHER_AREA}>其他（自己填）</option>
        </select>
      </div>
      {otherArea && (
        <input
          className={input}
          placeholder="填写地区"
          value={form.area}
          onChange={(e) => set("area", e.target.value)}
        />
      )}
      <div className="flex gap-2">
        <input
          className={input}
          type="number"
          placeholder="预算下限"
          value={form.budget_min}
          onChange={(e) => set("budget_min", e.target.value)}
        />
        <input
          className={input}
          type="number"
          placeholder="预算上限"
          value={form.budget_max}
          onChange={(e) => set("budget_max", e.target.value)}
        />
      </div>
      <label className="text-sm flex items-center gap-2">
        <input
          type="checkbox"
          checked={form.has_pets}
          onChange={(e) => set("has_pets", e.target.checked)}
        />
        有宠物 / 可养宠物
      </label>

      <div>
        <label className="text-sm text-gray-600 block mb-1">生活习惯标签（每行一个）</label>
        <textarea
          className={`${input} h-24`}
          placeholder={"🚭 不抽烟\n🚫 不带异性回家"}
          value={form.highlights}
          onChange={(e) => set("highlights", e.target.value)}
        />
      </div>

      <textarea
        className={`${input} h-32`}
        placeholder="详细描述…"
        required
        value={form.raw_text}
        onChange={(e) => set("raw_text", e.target.value)}
      />

      <div>
        <label className="text-sm text-gray-600 block mb-1">房屋图片</label>
        <input type="file" accept="image/*" multiple onChange={onFiles} className="text-sm" />
        {uploadImage.isPending && <span className="ml-2 text-xs text-gray-400">上传中…</span>}
        {images.length > 0 && (
          <div className="grid grid-cols-4 gap-2 mt-2">
            {images.map((src) => (
              <div key={src} className="relative">
                <img src={src} alt="房屋图片" className="w-full h-20 object-cover rounded border" />
                <button
                  type="button"
                  onClick={() => setImages((prev) => prev.filter((s) => s !== src))}
                  className="absolute -top-1 -right-1 bg-black/60 text-white rounded-full w-5 h-5 text-xs"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <select
          className={input}
          value={form.contact_type}
          onChange={(e) => set("contact_type", e.target.value)}
        >
          <option value="wechat">微信</option>
          <option value="phone">电话</option>
          <option value="xhs">小红书</option>
          <option value="email">邮箱</option>
        </select>
        <input
          className={input}
          placeholder="更新联系方式（留空则不变）"
          value={form.contact_value}
          onChange={(e) => set("contact_value", e.target.value)}
        />
      </div>

      <button
        type="submit"
        disabled={edit.isPending}
        className="px-4 py-2 rounded bg-nest text-white hover:bg-nest-dark disabled:opacity-50"
      >
        {edit.isPending ? "保存中…" : "保存修改"}
      </button>
    </form>
  );
}
