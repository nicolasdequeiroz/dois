document.addEventListener('DOMContentLoaded', () => {
  const wrapper = document.getElementById('slider-wrapper');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  if (!wrapper || !btnPrev || !btnNext) return;

  const moveSlider = (direction) => {
    const cards = Array.from(wrapper.children);
    if (cards.length === 0) return;

    const wrapperLeft = wrapper.getBoundingClientRect().left;
    const currentScrollPos = wrapper.scrollLeft;
    let targetScrollPos = currentScrollPos;

    if (direction === 1) {
      const nextCard = cards.find(
        (card) => card.getBoundingClientRect().left - wrapperLeft > 5
      );
      if (nextCard) {
        targetScrollPos =
          currentScrollPos + (nextCard.getBoundingClientRect().left - wrapperLeft);
      } else {
        targetScrollPos = currentScrollPos + (cards[0]?.offsetWidth || 0);
      }
    } else if (direction === -1) {
      const reverseCards = [...cards].reverse();
      const prevCard = reverseCards.find(
        (card) => card.getBoundingClientRect().left - wrapperLeft < -5
      );
      if (prevCard) {
        targetScrollPos =
          currentScrollPos + (prevCard.getBoundingClientRect().left - wrapperLeft);
      } else {
        targetScrollPos = currentScrollPos - (cards[0]?.offsetWidth || 0);
      }
    }

    wrapper.scrollBy({
      left: targetScrollPos - currentScrollPos,
      behavior: 'smooth',
    });
  };

  btnNext.addEventListener('click', () => moveSlider(1));
  btnPrev.addEventListener('click', () => moveSlider(-1));
});
