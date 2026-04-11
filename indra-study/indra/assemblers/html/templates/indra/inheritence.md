The file template.html in this directory is template base for several files. See
the diagram below for the inheritance structure. If you make changes to
template.html, be sure to check all the files that inherit from it to make sure
they still work as expected.

These files are currently in active use, however there are more files that
inherit from template.html that are not currently in use.
- search.html is the template used for https://db.indra.bio
- search_statements.html is the template used for https://db.indra.bio/statements
- statements_view.html is the template used in the HtmlAssembler class in indra.
- idbr_statements_view.html is the template used for https://db.indra.bio/statements/from...

```mermaid
graph LR
    A[indra: template.html] --> B[indra_db: idbr_template.html]
    A --> C[indra: statements_view.html - serves HtmlAssembler]
    C --> D[indra_db: idbr_statements_view.html - serves db.indra.bio/statements/from...]
    B --> E[indra_db: search.html - serves db.indra.bio]
    B --> F[indra_db: search_statements.html - serves db.indra.bio/statements search]
```
