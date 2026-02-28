import type { ReactNode } from 'react'

export function TabButton(props: {
  active: boolean
  onClick: () => void
  children: ReactNode
}) {
  return (
    <button
      className={`tabButton ${props.active ? 'tabButtonActive' : ''}`}
      onClick={props.onClick}
      type="button"
    >
      {props.children}
    </button>
  )
}

