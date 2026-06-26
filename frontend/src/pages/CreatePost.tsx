import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useCreatePost } from "../api/hooks";

export default function CreatePost() {
  const navigate = useNavigate();
  const createPost = useCreatePost();
  const [form, setForm] = useState({
    title: "",
    intent: "seeking",
    area: "",
    budget_min: "",
    budget_max: "",
    mbti: "",
    has_pets: false,
    contact_type: "wechat",
    contact_value: "",
    raw_text: "",
  });

  function set<K extends keyof typeof form>(key: K, v: (typeof form)[K]) {
    setForm({ ...form, [key]: v });
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    await createPost.mutateAsync({
      title: form.title || null,
      intent: form.intent,
      area: form.area || null,
      budget_min: form.budget_min ? Number(form.budget_min) : null,
      budget_max: form.budget_max ? Number(form.budget_max) : null,
      mbti: form.mbti || null,
      has_pets: form.has_pets,
      contact_type: form.contact_type,
      contact_value: form.contact_value,
      raw_text: form.raw_text,
    });
    navigate("/");
  }

  const input = "border rounded px-3 py-2 text-sm w-full";

  return (
    <form onSubmit={submit} className="max-w-xl mx-auto bg-white border rounded-lg p-6 space-y-3">
      <h1 className="text-lg font-semibold">发布求租 / 招租帖</h1>
      <p className="text-xs text-gray-400">提交后会进入人工审核，通过后展示。</p>

      <input
        className={input}
        placeholder="标题"
        value={form.title}
        onChange={(e) => set("title", e.target.value)}
      />
      <div className="flex gap-2">
        <select
          className={input}
          value={form.intent}
          onChange={(e) => set("intent", e.target.value)}
        >
          <option value="seeking">求租</option>
          <option value="offering">招租</option>
        </select>
        <input
          className={input}
          placeholder="地区，如 North York"
          value={form.area}
          onChange={(e) => set("area", e.target.value)}
        />
      </div>
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
        <input
          className={input}
          placeholder="MBTI"
          value={form.mbti}
          onChange={(e) => set("mbti", e.target.value.toUpperCase())}
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
          placeholder="联系方式"
          required
          value={form.contact_value}
          onChange={(e) => set("contact_value", e.target.value)}
        />
      </div>
      <textarea
        className={`${input} h-32`}
        placeholder="详细描述…"
        required
        value={form.raw_text}
        onChange={(e) => set("raw_text", e.target.value)}
      />

      <button
        type="submit"
        disabled={createPost.isPending}
        className="px-4 py-2 rounded bg-nest text-white hover:bg-nest-dark disabled:opacity-50"
      >
        {createPost.isPending ? "提交中…" : "提交审核"}
      </button>
    </form>
  );
}
