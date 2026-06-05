import { useEffect, useRef, useState, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Edges, Environment } from '@react-three/drei'
import * as THREE from 'three'
import './App.css'

function MechanicalPart() {
  const metalMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: "#b0b5b9",
    metalness: 1.0,
    roughness: 0.15,
  }), [])
  
  return (
    <group>
      {/* Main outer gear/bearing body */}
      <mesh material={metalMaterial} rotation={[Math.PI/2, 0, 0]}>
        <torusGeometry args={[1.5, 0.4, 32, 64]} />
      </mesh>
      {/* Inner shaft */}
      <mesh material={metalMaterial} rotation={[Math.PI/2, 0, 0]}>
        <cylinderGeometry args={[0.6, 0.6, 1.2, 32]} />
      </mesh>
      {/* Hole inside shaft */}
      <mesh rotation={[Math.PI/2, 0, 0]} position={[0, 0.01, 0]}>
        <cylinderGeometry args={[0.4, 0.4, 1.22, 32]} />
        <meshBasicMaterial color="#111" />
      </mesh>
      {/* Spokes connecting them */}
      {[0, 1, 2, 3, 4, 5, 6, 7].map(i => (
        <mesh key={i} material={metalMaterial} rotation={[0, 0, (i * Math.PI) / 4]}>
          <cylinderGeometry args={[0.15, 0.15, 3, 16]} />
        </mesh>
      ))}
    </group>
  )
}

function ModernArchitecture() {
  const glassMaterial = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: "#e6f2ff",
    metalness: 0.1,
    roughness: 0.1,
    transmission: 0.9, 
    ior: 1.5,
    thickness: 0.5,
    envMapIntensity: 1.5
  }), [])

  const concreteMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: "#d0d0d0",
    metalness: 0.2,
    roughness: 0.8
  }), [])

  return (
    <group position={[0, -2.5, 0]}>
      {/* Base Foundation Plaza */}
      <mesh material={concreteMaterial} position={[0, 0.25, 0]}>
        <boxGeometry args={[5, 0.5, 5]} />
      </mesh>
      
      {/* Main Skyscraper (10 floors) */}
      {[...Array(10)].map((_, i) => (
        <group key={`floor-main-${i}`} position={[-0.8, 0.5 + i * 0.45, -0.8]}>
          <mesh material={glassMaterial}>
            <boxGeometry args={[1.4, 0.4, 1.4]} />
          </mesh>
          <mesh material={concreteMaterial} position={[0, 0.2, 0]}>
            <boxGeometry args={[1.5, 0.05, 1.5]} />
          </mesh>
        </group>
      ))}

      {/* Helipad on Main Skyscraper */}
      <mesh material={concreteMaterial} position={[-0.8, 0.5 + 10 * 0.45, -0.8]}>
        <cylinderGeometry args={[0.5, 0.5, 0.1, 32]} />
      </mesh>

      {/* Secondary Skyscraper (10 floors - Identical Twin) */}
      {[...Array(10)].map((_, i) => (
        <group key={`floor-sec-${i}`} position={[1.2, 0.5 + i * 0.45, 1.0]}>
          <mesh material={glassMaterial}>
            <boxGeometry args={[1.4, 0.4, 1.4]} />
          </mesh>
          <mesh material={concreteMaterial} position={[0, 0.2, 0]}>
            <boxGeometry args={[1.5, 0.05, 1.5]} />
          </mesh>
        </group>
      ))}

      {/* Helipad on Secondary Skyscraper */}
      <mesh material={concreteMaterial} position={[1.2, 0.5 + 10 * 0.45, 1.0]}>
        <cylinderGeometry args={[0.5, 0.5, 0.1, 32]} />
      </mesh>

      {/* Modern Glass Pavilion */}
      <mesh material={glassMaterial} position={[0.5, 0.8, -1.5]}>
        <boxGeometry args={[2.5, 0.6, 1.5]} />
      </mesh>
    </group>
  )
}

function HologramScene({ landmarks, modelIdx }: { landmarks: any, modelIdx: number }) {
  const meshRef = useRef<THREE.Group>(null)
  
  const targetRot = useRef({ x: 0, y: 0 })
  const currentRot = useRef({ x: 0, y: 0 })
  const targetScale = useRef(0.8) // Moved models back
  const currentScale = useRef(0.8)

  useFrame((state, delta) => {
    if (meshRef.current) {
      if (landmarks && landmarks.length > 0) {
        const hand = landmarks[0]
        const x = hand[0].x - 0.5
        const y = hand[0].y - 0.5
        
        targetRot.current.y = -x * Math.PI * 3
        targetRot.current.x = y * Math.PI * 2

        const thumb = hand[4]
        const index = hand[8]
        if (thumb && index) {
          const dist = Math.hypot(thumb.x - index.x, thumb.y - index.y)
          targetScale.current = dist < 0.06 ? 1.5 : 0.8 // Updated scale limits
        }
      } else {
        targetRot.current.y += delta * 0.5
      }

      currentRot.current.x += (targetRot.current.x - currentRot.current.x) * 0.1
      currentRot.current.y += (targetRot.current.y - currentRot.current.y) * 0.1
      currentScale.current += (targetScale.current - currentScale.current) * 0.1

      meshRef.current.rotation.x = currentRot.current.x
      meshRef.current.rotation.y = currentRot.current.y
      meshRef.current.scale.setScalar(currentScale.current)
    }
  })

  return (
    <>
      {(modelIdx === 1 || modelIdx === 2) && <Environment preset="city" />}
      <ambientLight intensity={(modelIdx === 1 || modelIdx === 2) ? 1 : 0.5} />
      <directionalLight position={[10, 10, 10]} intensity={(modelIdx === 1 || modelIdx === 2) ? 2 : 1.5} />
      <group ref={meshRef}>
        {modelIdx === 0 && (
          <mesh>
            <icosahedronGeometry args={[1.5, 0]} />
            <meshStandardMaterial color="#f4c244" flatShading={true} roughness={0.5} />
            <Edges scale={1.02} threshold={1} color="#111111" />
          </mesh>
        )}
        {modelIdx === 1 && <MechanicalPart />}
        {modelIdx === 2 && <ModernArchitecture />}
      </group>
    </>
  )
}

const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4], // Thumb
  [0, 5], [5, 6], [6, 7], [7, 8], // Index
  [5, 9], [9, 10], [10, 11], [11, 12], // Middle
  [9, 13], [13, 14], [14, 15], [15, 16], // Ring
  [13, 17], [0, 17], [17, 18], [18, 19], [19, 20] // Pinky
];

const XSymbol = () => (
  <svg viewBox="0 0 100 100" className="ttt-symbol x-symbol">
    <path d="M 20 20 L 80 80 M 80 20 L 20 80" stroke="currentColor" strokeWidth="12" strokeLinecap="square" />
  </svg>
)

const OSymbol = () => (
  <svg viewBox="0 0 100 100" className="ttt-symbol o-symbol">
    <circle cx="50" cy="50" r="32" stroke="currentColor" strokeWidth="12" fill="none" />
  </svg>
)

const GESTURE_EMOJIS: Record<string, string> = {
  "THUMBS_UP":  "👍",
  "PEACE":      "✌️",
  "OPEN_HAND":  "🖐️",
  "FIST":       "👊",
  "POINTING":   "🫵",
  "PENGUIN_FLOWERS": "💖",
  "DOG_HEART":  "💖",
  "SHY_FINGERS": "👉👈",
  "CALL_ME":    "🤙",
  "THUMBS_DOWN": "👎",
  "GLASSES":    "🤓",
  "ITALIAN":    "🤌",
  "SHH":        "🤫",
}

function ParticleSystem({ gesture }: { gesture: string | null }) {
  const [particles, setParticles] = useState<any[]>([])

  useEffect(() => {
    if (!gesture || gesture === "NONE") {
      setParticles([])
      return
    }
    const emoji = GESTURE_EMOJIS[gesture]
    if (!emoji) return

    const interval = setInterval(() => {
      setParticles(p => {
        // Randomly choose left or right side of the screen
        const isLeft = Math.random() > 0.5;
        const xPos = isLeft 
          ? 2 + Math.random() * 15   // 2vw to 17vw (Left side)
          : 83 + Math.random() * 15; // 83vw to 98vw (Right side)

        return [...p, {
          id: Date.now() + Math.random(),
          x: xPos,
          emoji,
          size: 50 + Math.random() * 50 // Larger emojis (50px to 100px)
        }].slice(-8) // Allow up to 8 simultaneous particles
      })
    }, 450) // Slower spawn rate

    return () => clearInterval(interval)
  }, [gesture])

  return (
    <div className="particles-container">
      {particles.map(p => (
        <div key={p.id} className="particle" style={{ left: `${p.x}vw`, fontSize: `${p.size}px` }}>
          {p.emoji}
        </div>
      ))}
    </div>
  )
}

function App() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  
  const [mode, setMode] = useState<"MEMES" | "TICTACTOE" | "3D_VIEWER">("3D_VIEWER")
  const [gestureData, setGestureData] = useState<any>(null)
  const [modelIdx, setModelIdx] = useState(0)

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
      .then(stream => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.play()
        }
      })

    const ws = new WebSocket("ws://localhost:8000/ws")
    ws.onopen = () => console.log("WS Connected")
    ws.onmessage = (e) => setGestureData(JSON.parse(e.data))
    wsRef.current = ws

    return () => ws.close()
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN && videoRef.current && canvasRef.current) {
        const ctx = canvasRef.current.getContext('2d')
        if (ctx) {
          ctx.drawImage(videoRef.current, 0, 0, 640, 480)
          const dataUrl = canvasRef.current.toDataURL("image/jpeg", 0.5)
          wsRef.current.send(JSON.stringify({ mode, image: dataUrl, width: 640, height: 480 }))
        }
      }
    }, 100)

    return () => clearInterval(interval)
  }, [mode])

  const GESTURE_TO_FILE: Record<string, string> = {
    "THUMBS_UP":  "hamster_thumbsup.jpg",
    "PEACE":      "hamster_peace.jpg",
    "OPEN_HAND":  "hamster_open.jpg",
    "FIST":       "hamster_fist.jpg",
    "POINTING":   "monkey_pointing.jpeg",
    "PENGUIN_FLOWERS": "penguin-flowers.jpg",
    "DOG_HEART":  "dog-heart.jpg",
    "SHY_FINGERS": "cat-fingers-touching.jpg",
    "CALL_ME":    "cat-phone-signal.jpg",
    "THUMBS_DOWN": "sad-hamster.jpg",
    "GLASSES":    "cat-glasses.jpg",
    "ITALIAN":    "cat-doubt.jpg",
    "SHH":        "cat-shh.jpg",
  }

  const memeSrc = gestureData?.gesture && gestureData.gesture !== "NONE" ? `/memes/${GESTURE_TO_FILE[gestureData.gesture]}` : null

  return (
    <div className="app-container">
      <ParticleSystem gesture={mode === "MEMES" ? gestureData?.gesture : null} />
      
      <header className="header">
        <h1>GesTracker</h1>
        <div className="mode-toggle">
          <button className={mode === "MEMES" ? "active" : ""} onClick={() => setMode("MEMES")}>
            Modo Memes
          </button>
          <button className={mode === "TICTACTOE" ? "active" : ""} onClick={() => setMode("TICTACTOE")}>
            3 en Raya
          </button>
          <button className={mode === "3D_VIEWER" ? "active" : ""} onClick={() => setMode("3D_VIEWER")}>
            Visor 3D
          </button>
        </div>
      </header>

      <main className="main-content">
        <div className="left-section">
          <h2 className="hero-text">
            {mode === "MEMES" ? "¡Detectando Memes!" : mode === "TICTACTOE" ? "¡Juega contra la IA!" : "Manipulador 3D"}
          </h2>
          
          <div className="video-wrapper">
            <video ref={videoRef} className="webcam" muted playsInline />
            <canvas ref={canvasRef} width={640} height={480} style={{ display: 'none' }} />

            {mode === "TICTACTOE" && gestureData?.tictactoe && (
              <div className="tictactoe-overlay">
                 <div className="grid">
                   {gestureData.tictactoe.board.map((row: any, r: number) => 
                     row.map((cell: string, c: number) => (
                       <div key={`${r}-${c}`} className="cell">
                         {cell === 'X' ? <XSymbol /> : cell === 'O' ? <OSymbol /> : null}
                       </div>
                     ))
                   )}
                 </div>
                 
                 {gestureData.tictactoe.game_over && (
                   <div className="game-over">
                     <h2>{gestureData.tictactoe.winner === 'Tie' ? '¡Empate!' : `¡Ganador: ${gestureData.tictactoe.winner}!`}</h2>
                     <p>Haz pinza para reiniciar</p>
                   </div>
                 )}

                 {gestureData.tictactoe.cursor.x >= 0 && (
                   <div 
                     className={`cursor ${gestureData.tictactoe.cursor.pinching ? 'pinching' : ''}`}
                     style={{
                       left: `${gestureData.tictactoe.cursor.x * 100}%`,
                       top: `${gestureData.tictactoe.cursor.y * 100}%`
                     }}
                   />
                 )}
              </div>
            )}

            <svg className="landmarks-overlay" viewBox="0 0 1 1">
              {gestureData?.landmarks?.map((hand: any[], hIdx: number) => (
                <g key={hIdx}>
                  {HAND_CONNECTIONS.map(([start, end], i) => (
                    <line 
                      key={`line-${i}`}
                      x1={hand[start].x} y1={hand[start].y}
                      x2={hand[end].x} y2={hand[end].y}
                      stroke="#111" strokeWidth="0.005" strokeLinecap="round"
                    />
                  ))}
                  {hand.map((lm, i) => (
                    <circle key={i} cx={lm.x} cy={lm.y} r="0.010" fill="#fff" stroke="#111" strokeWidth="0.004" />
                  ))}
                </g>
              ))}
            </svg>
          </div>

          {mode === "3D_VIEWER" && (
            <div className="instructions-panel">
               <h3>🕹️ Controles 3D</h3>
               <div className="control-item">
                 <span className="gesture-icon">✊</span>
                 <div>
                   <h4>Mover Modelo</h4>
                   <p>Cierra el puño y mueve la mano en el aire.</p>
                 </div>
               </div>
               <div className="control-item">
                 <span className="gesture-icon">🤏</span>
                 <div>
                   <h4>Hacer Zoom</h4>
                   <p>Junta tu dedo índice y pulgar (gesto de Pinza).</p>
                 </div>
               </div>
            </div>
          )}
        </div>

        {mode === "MEMES" && (
          <div className="side-panel">
            {memeSrc ? (
              <div className="meme-card">
                <img src={memeSrc} alt="Meme" />
                <div className="meme-label">{gestureData.label}</div>
              </div>
            ) : (
              <div className="placeholder">
                <p>Esperando gesto...</p>
                <span>👍 ✌️ 🖐️ 👊 🫵 💖 👉👈 🤙 👎 🤓 🤌 🤫</span>
              </div>
            )}
          </div>
        )}
        
        {mode === "TICTACTOE" && (
           <div className="side-panel rules-panel">
             <h2>Instrucciones</h2>
             <ul>
                <li>Tú juegas con las <b>X</b>.</li>
                <li>La IA juega con las <b>O</b>.</li>
                <li>Mueve tu dedo índice para apuntar.</li>
                <li>Haz pinza (junta índice y pulgar) para marcar.</li>
                <li>¡Buena suerte!</li>
             </ul>
           </div>
        )}

        {mode === "3D_VIEWER" && (
           <div className="side-panel" style={{ padding: 0, overflow: 'hidden', background: '#f0ead6', position: 'relative' }}>
             
             <button 
               onClick={() => setModelIdx(prev => (prev === 0 ? 2 : prev - 1))} 
               style={{ position: 'absolute', top: '50%', left: 20, zIndex: 10, transform: 'translateY(-50%)', background: '#111', color: '#fff', border: 'none', borderRadius: '50%', width: 50, height: 50, cursor: 'pointer', fontSize: 24, boxShadow: '4px 4px 0px #f4c244' }}>
               ←
             </button>

             <button 
               onClick={() => setModelIdx(prev => (prev === 2 ? 0 : prev + 1))} 
               style={{ position: 'absolute', top: '50%', right: 20, zIndex: 10, transform: 'translateY(-50%)', background: '#111', color: '#fff', border: 'none', borderRadius: '50%', width: 50, height: 50, cursor: 'pointer', fontSize: 24, boxShadow: '4px 4px 0px #f4c244' }}>
               →
             </button>

             <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
               <HologramScene landmarks={gestureData?.landmarks} modelIdx={modelIdx} />
             </Canvas>
             
             <div style={{ position: 'absolute', bottom: 30, left: 0, width: '100%', textAlign: 'center' }}>
               <span style={{ background: '#111', color: '#f4c244', padding: '10px 20px', borderRadius: '100px', fontWeight: 800, border: '3px solid #111', boxShadow: '4px 4px 0px 0px #111' }}>
                 {modelIdx === 0 ? "FIGURA NEO-BRUTALISTA" : modelIdx === 1 ? "ROTOR MECÁNICO" : "MAQUETA ARQUITECTÓNICA"}
               </span>
             </div>
           </div>
        )}
      </main>
    </div>
  )
}

export default App
