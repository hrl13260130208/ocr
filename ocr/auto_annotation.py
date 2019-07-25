from lxml import etree, objectify

E = objectify.ElementMaker(annotate=False)
anno_tree = E.annotation(
    E.folder('png'),
    E.filename("page_0"),
    E.path("C:/temp/png/page_0.jpg"),
    E.source(
        E.database("Unknown")
    ),
    E.size(
        E.width(1653),
        E.height(2339),
        E.depth(1)
    ),
    E.segmented(0),
    E.object(
        E.name("title"),
        E.pose("Unspecified"),
        E.truncated(0),
        E.Difficult(0),
        E.bndbox(
            E.xmin(100),
            E.ymin(200),
            E.xmax(300),
            E.ymax(400)
        )
    )

)
anno_tree.set("verified","no")
etree.ElementTree(anno_tree).write("C:/temp/png/page_0.xml", pretty_print=True)
