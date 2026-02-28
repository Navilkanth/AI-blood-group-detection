import './App.css'
import { useMemo, useState } from 'react'
import { TabButton } from './components/TabButton'
import { BloodGroupPredictor } from './features/BloodGroupPredictor'
import { CellsAnalyzer } from './features/CellsAnalyzer'
import { HemoglobinCheck } from './features/HemoglobinCheck'

import { History } from './features/History'

function App() {
  const [tab, setTab] = useState<'blood' | 'hb' | 'cells' | 'history'>('blood')
  const subtitle = useMemo(() => {
    if (tab === 'blood') return 'ABO prediction with multi-agent cross-verification'
    if (tab === 'hb') return 'Reference range check'
    if (tab === 'cells') return 'RBC/WBC rough estimate (demo)'
    return 'Database records stored in MongoDB Atlas'
  }, [tab])

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brandTitle">AI Blood Group Detection</div>
          <div className="brandSubtitle">{subtitle}</div>
        </div>
        <nav className="tabs">
          <TabButton active={tab === 'blood'} onClick={() => setTab('blood')}>
            Blood group
          </TabButton>
          <TabButton active={tab === 'hb'} onClick={() => setTab('hb')}>
            Hemoglobin
          </TabButton>
          <TabButton active={tab === 'cells'} onClick={() => setTab('cells')}>
            RBC / WBC
          </TabButton>
          <TabButton active={tab === 'history'} onClick={() => setTab('history')}>
            History
          </TabButton>
        </nav>
      </header>

      <main className="main">
        {tab === 'blood' ? <BloodGroupPredictor /> : null}
        {tab === 'hb' ? <HemoglobinCheck /> : null}
        {tab === 'cells' ? <CellsAnalyzer /> : null}
        {tab === 'history' ? <History /> : null}
      </main>

      <footer className="footer">
        <div className="muted small">
          AI-assisted preliminary screening only. Always confirm via certified laboratory testing.
        </div>
      </footer>
    </div>
  )
}

export default App
