document.getElementById('fetch_msg').addEventListener('click', () => {
    fetch('/api/message')
        .then(response => {
            if (!response.ok) {
                throw new error("server responded with error")
            }
            return response.text()
        })
        .then(data => {
            document.getElementById('msg').innerText = data
        })
        .catch(error => {
            console.log("error", error)
            document.getElementById('msg').innerText = "handling error"
        })


})

