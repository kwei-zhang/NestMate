export default function Login() {
  // Backend handles the OAuth handshake and redirects back with tokens.
  const googleUrl = "/api/auth/google/login";
  const wechatUrl = "/api/auth/wechat/login";

  return (
    <div className="max-w-sm mx-auto bg-white rounded-lg border p-8 mt-8 space-y-4 text-center">
      <h1 className="text-xl font-semibold">登录 NestMate</h1>
      <p className="text-sm text-gray-500">登录后即可查看房源联系方式、收藏和发帖</p>

      <a
        href={googleUrl}
        className="flex items-center justify-center gap-2 border rounded-lg py-2.5 hover:bg-gray-50"
      >
        <span className="font-medium">使用 Google 登录</span>
      </a>
      <a
        href={wechatUrl}
        className="flex items-center justify-center gap-2 rounded-lg py-2.5 bg-[#07c160] text-white hover:opacity-90"
      >
        <span className="font-medium">使用微信登录</span>
      </a>
    </div>
  );
}
