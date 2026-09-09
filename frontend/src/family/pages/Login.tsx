import type { Role } from '../types'
import { Card, Icon } from '../ui'

// 登录页：对应原型「1-登录页」（品牌徽标 / 角色选择 / 微信绿登录 / 隐私盾卡）

const ROLES: Role[] = ['家属', '管理员', '老人']

export default function Login({ role, onRole, onLogin }: { role: Role; onRole: (r: Role) => void; onLogin: () => void }) {
  return (
    <div className="flex flex-1 flex-col items-center overflow-y-auto bg-fam-bg px-8 pb-10">
      <div className="mt-16 flex h-20 w-20 items-center justify-center rounded-[22px] bg-fam-teal">
        <Icon name="pulse" size={40} color="#fff" sw={2.2} />
      </div>
      <div className="mt-5 text-[22px] text-[#1A2027]">智能康养监测系统</div>
      <div className="mt-1.5 text-[13px] text-[#6B7280]">家属端 · 让牵挂看得见</div>

      <div className="mt-8 flex w-full gap-2.5">
        {ROLES.map((r) => (
          <button
            key={r}
            onClick={() => onRole(r)}
            className={`h-10 flex-1 rounded-full text-[13px] transition-colors ${
              role === r ? 'bg-fam-teal text-white' : 'border border-[#E8ECF1] bg-white text-[#6B7280]'
            }`}
          >
            {r}
          </button>
        ))}
      </div>

      <button
        onClick={onLogin}
        className="mt-6 flex h-12 w-full items-center justify-center gap-2 rounded-full bg-fam-green text-base text-white active:bg-[#06a956]"
      >
        <Icon name="smile" size={18} color="#fff" />
        微信一键登录
      </button>
      <p className="mt-3 text-[11px] text-[#9AA3AD]">以「{role}」身份进入（演示环境，无需真实授权）</p>

      <Card className="mt-8 flex w-full items-center gap-3 p-4">
        <Icon name="shield" size={22} color="#10B9A8" />
        <div className="text-[11px] leading-relaxed text-[#6B7280]">
          数据端侧处理 · 画面不上云 · 隐私优先
          <br />
          关键预警始终送达，守护不打烊
        </div>
      </Card>
    </div>
  )
}
