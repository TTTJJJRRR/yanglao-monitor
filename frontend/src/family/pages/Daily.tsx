import { dailyCards } from '../data'
import { Card, Icon, SubNav } from '../ui'

// 安心日报：对应原型「6-安心日报」（青绿主卡 + 四项指标 + 分享）

export default function Daily({ onBack, onShare }: { onBack: () => void; onShare: () => void }) {
  const today = new Date()
  const yesterday = new Date(today.getTime() - 86400000)

  return (
    <div className="flex-1 overflow-y-auto bg-fam-bg">
      <SubNav
        title="安心日报"
        onBack={onBack}
        right={
          <button onClick={onShare} aria-label="分享">
            <Icon name="share" size={18} color="#6B7280" />
          </button>
        }
      />
      <div className="space-y-3.5 px-4 py-4">
        {/* 青绿渐变安心主卡（原型同款） */}
        <div className="rounded-2xl bg-gradient-to-br from-[#10B9A8] to-[#0B8C80] p-5 text-white">
          <div className="flex items-center gap-3">
            <Icon name="smile" size={40} color="#fff" sw={1.3} />
            <div>
              <div className="text-lg">今日一切安好</div>
              <div className="mt-1 text-xs text-white/85">
                {yesterday.getMonth() + 1}月{yesterday.getDate()}日 · 父亲的昨日报告
              </div>
            </div>
          </div>
          <div className="mt-4 rounded-xl bg-white/15 px-3 py-2 text-xs text-white/90">
            体征平稳 · 活动正常 · 睡眠良好 · 无异常事件
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2.5">
          {dailyCards.map((c) => (
            <Card key={c.title} className="p-3.5">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-full bg-[#E2F5F2]">
                <Icon name={c.icon} size={16} color="#0B8C80" />
              </div>
              <div className="text-sm text-[#1A2027]">{c.title}</div>
              <div className="mt-1 text-[11px] leading-relaxed text-[#9AA3AD]">{c.desc}</div>
            </Card>
          ))}
        </div>

        <button
          onClick={onShare}
          className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-fam-green text-sm text-white active:bg-[#06a956]"
        >
          <Icon name="share" size={16} color="#fff" />
          分享给家人
        </button>
        <p className="text-center text-[11px] text-[#9AA3AD]">日报每日 08:00 自动生成（演示数据）</p>
      </div>
    </div>
  )
}
