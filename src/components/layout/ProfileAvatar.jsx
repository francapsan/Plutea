import { useRef, useState } from 'react'
import './ProfileAvatar.css'

const STORAGE_KEY = 'plutea.profilePhoto'

export function ProfileAvatar() {
  const inputRef = useRef(null)
  const [photo, setPhoto] = useState(() => localStorage.getItem(STORAGE_KEY))

  async function handleFileChange(event) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file || !file.type.startsWith('image/')) return

    try {
      const dataUrl = await cropToSquare(file)
      setPhoto(dataUrl)
      localStorage.setItem(STORAGE_KEY, dataUrl)
    } catch {
      return
    }
  }

  return (
    <div className="profile-avatar">
      <button
        type="button"
        className="profile-avatar__button"
        onClick={() => inputRef.current?.click()}
        aria-label={photo ? 'Cambiar foto de perfil' : 'Añadir foto de perfil'}
        title="Cambiar foto de perfil"
      >
        {photo ? (
          <img src={photo} alt="" />
        ) : (
          <span className="profile-avatar__placeholder" aria-hidden="true" />
        )}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="visually-hidden"
        tabIndex={-1}
        aria-hidden="true"
        onChange={handleFileChange}
      />
    </div>
  )
}

function cropToSquare(file) {
  return new Promise((resolve, reject) => {
    const image = new Image()
    const objectUrl = URL.createObjectURL(file)

    image.onload = () => {
      const size = 256
      const canvas = document.createElement('canvas')
      canvas.width = size
      canvas.height = size
      const context = canvas.getContext('2d')
      const side = Math.min(image.width, image.height)
      const sourceX = (image.width - side) / 2
      const sourceY = (image.height - side) / 2
      context.drawImage(image, sourceX, sourceY, side, side, 0, 0, size, size)
      URL.revokeObjectURL(objectUrl)
      resolve(canvas.toDataURL('image/jpeg', 0.86))
    }

    image.onerror = () => {
      URL.revokeObjectURL(objectUrl)
      reject(new Error('No se pudo leer la imagen'))
    }

    image.src = objectUrl
  })
}
