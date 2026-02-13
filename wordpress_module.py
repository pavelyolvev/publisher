import wordpress

site = "https://pavelyolvevwpsite.wordpress.com"


def login_wp(site, login, password):
    wp = wordpress.Connect(site, login, password)
    return wp.page.fetch_all_pages()
