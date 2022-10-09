let updateButtons = document.getElementsByClassName('like-product')

for (let i = 0; i < updateButtons.length; i++) {
    updateButtons[i].addEventListener('click', function () {
        let productId = this.dataset.product;
        let action = this.dataset.action;
        addLikedProduct(productId, action)
    })
}

function addLikedProduct(productId, action){

    let url = '/like_item/'

    fetch(url, {method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })

        .then((response) =>{
            return response.json()
        })
        .then((data) =>{
            console.log(data)
            location.reload()
        })
}