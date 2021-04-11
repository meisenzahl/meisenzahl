#!/usr/bin/env python3

import github
import jinja2
import markdown
import os

def get_pull_requests_created_by(client, organization, username, state, verbose=True):
    prs = []

    for repo in client.get_organization(organization).get_repos():
        for pr in repo.get_pulls(state=state):
            login = pr.user.login
            if login == username:
                if state == "closed" and not pr.merged:
                    continue

                link = markdown.markdown("<a href=\"{}\">{}/{} #{} · {}</a>".format(
                    pr.html_url,
                    organization,
                    repo.name,
                    pr.number,
                    pr.title,
                ))

                prs.append({
                    "org": organization,
                    "repo": repo.name,
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "updated_at": pr.updated_at,
                    "link": link,
                    "draft": pr.draft,
                    "mergeable": pr.mergeable,
                })

                if verbose:
                    print("{}: {}/{} #{} · {}".format(
                        state,
                        organization,
                        repo.name,
                        pr.number,
                        pr.title,
                    ))

    return prs

def main():
    GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN", "")
    GITHUB_USER = os.environ.get("GITHUB_USER", "")

    client = github.Github(GITHUB_ACCESS_TOKEN)

    context = {
        "open": [],
        "merged": [],
        "upstream": [],
    }

    context["open"] = get_pull_requests_created_by(client, "elementary", GITHUB_USER, "open")
    context["merged"] = get_pull_requests_created_by(client, "elementary", GITHUB_USER, "closed")

    context["open"].sort(key=lambda pr: pr["updated_at"], reverse=True)
    context["merged"].sort(key=lambda pr: pr["updated_at"], reverse=True)

    context["upstream"].append({
        "link": '<a href="https://gitlab.gnome.org/GNOME/libhandy/-/merge_requests/671">GNOME/libhandy #671 · carousel-box: Invalidate cache for children size allocate</a>'
    })
    context["upstream"].append({
        "link": '<a href="https://gitlab.freedesktop.org/plymouth/plymouth/-/merge_requests/125">plymouth/plymouth #125 · Use fallback image if BGRT is not supported</a>'
    })

    template_text = open("README.md.jinja2", "r").read()
    template = jinja2.Template(template_text)
    text = template.render(context)

    f = open("README.md", "w")
    f.write(text)

if __name__ == "__main__":
    main()
