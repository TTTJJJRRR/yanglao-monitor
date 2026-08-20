import { useState } from 'react'
import { demoElders } from '../data/demo'
import { Btn, Card, EmptyHint } from '../components/ui'

// 老人档案：对应原型「8-老人档案」
// 演示数据：demoElders；搜索为真实前端过滤

export default function Elders() {
  const [keyword, setKeyword] = useState('')
  const list = demoElders.filter((e) => !keyword || e.name.includes(keyword) || e.bed.includes(keyword))

  return (
    <>
      <div className="flex items-center justify-between">
        <div className="flex h-[38px] w-[280px] items-center gap-2 rounded-[10px] border border-line bg-white pl-3">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="7.5" cy="7.5" r="5" stroke="#A8AB9C" strokeWidth="1.5" />
            <path d="M11.5 11.5L14.5 14.5" stroke="#A8AB9C" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <input
            className="h-full flex-1 bg-transparent text-[13px] text-ink outline-none placeholder:text-ink-hint"
            placeholder="搜索姓名 / 床位"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
        </div>
        <Btn primary>+ 添加老人</Btn>
      </div>

      <Card className="overflow-hidden">
        <table className="w-full text-left">
          <thead>
            <tr className="h-12 bg-cream text-xs text-ink-sub">
              <th className="w-[180px] px-5 font-normal">姓名</th>
              <th className="w-[100px] font-normal">年龄</th>
              <th className="w-[120px] font-normal">床位</th>
              <th className="w-[250px] font-normal">健康标签</th>
              <th className="w-[260px] font-normal">家属联系人</th>
              <th className="font-normal">状态</th>
            </tr>
          </thead>
          <tbody>
            {list.map((e, i) => (
              <tr key={e.name} className={`h-14 text-[13px] ${i > 0 ? 'border-t border-[#F0EDE3]' : ''}`}>
                <td className="px-5 text-ink">{e.name}</td>
                <td className="text-ink-sub">{e.age} · {e.gender}</td>
                <td className="text-ink-sub">{e.bed}</td>
                <td className="text-ink-sub">{e.tags}</td>
                <td className="text-ink-sub">{e.contact}</td>
                <td className="text-sage-deep">● {e.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {list.length === 0 && <EmptyHint text={`没有匹配「${keyword}」的老人`} />}
      </Card>
    </>
  )
}
