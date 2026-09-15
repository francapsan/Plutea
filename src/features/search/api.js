export async function searchCatalog(query) {
  const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`)
  if (!response.ok) {
    throw new Error('No se pudo completar la búsqueda')
  }
  return response.json()
}

export async function fetchBook(bookId, fallback) {
  const params = new URLSearchParams()
  if (fallback && fallback.length <= 400) {
    params.set('fallback', fallback)
  }
  const suffix = params.size ? `?${params}` : ''
  const response = await fetch(`/api/books/${encodeURIComponent(bookId)}${suffix}`)
  if (!response.ok) {
    throw new Error('No se pudo cargar la ficha')
  }
  return response.json()
}
