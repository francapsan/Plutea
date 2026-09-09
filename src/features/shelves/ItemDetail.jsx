import './ItemDetail.css'

export function ItemDetail({ onClose }) {
  return (
    <aside className="item-detail" aria-label="Ficha de la obra">
      <header className="item-detail__header">
        <p className="item-detail__kicker">Ficha</p>
        <button type="button" className="item-detail__close" onClick={onClose}>
          Cerrar
        </button>
      </header>

      <div className="item-detail__cover" aria-hidden="true" />

      <div className="item-detail__fields">
        <div className="item-detail__line item-detail__line--title" />
        <div className="item-detail__line" />
        <div className="item-detail__line item-detail__line--short" />
      </div>

      <section className="item-detail__block">
        <h3>Reseña</h3>
        <div className="item-detail__note">
          <span />
          <span />
          <span />
        </div>
      </section>
    </aside>
  )
}
