import { PLACEHOLDER_SHELVES } from './placeholders'

const STORAGE_KEY = 'plutea.shelves'

export function emptyCollection() {
  return Object.fromEntries(PLACEHOLDER_SHELVES.map((shelf) => [shelf.id, []]))
}

export function loadCollection() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return emptyCollection()
    return { ...emptyCollection(), ...JSON.parse(raw) }
  } catch {
    return emptyCollection()
  }
}

export function saveCollection(collection) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(collection))
}

export function addBookToShelf(collection, shelfId, book) {
  const current = collection[shelfId] ?? []
  if (current.some((item) => item.id === book.id)) {
    return collection
  }
  return {
    ...collection,
    [shelfId]: [...current, book],
  }
}
