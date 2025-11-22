"use client";

import { useEffect, useState, useMemo } from "react";
import { Link } from "@/types";
import { getLinks, deleteLink } from "@/lib/api";

export default function Home() {
  const [links, setLinks] = useState<Link[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // state filtrage et recherche
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [resourceTypeFilter, setResourceTypeFilter] = useState<
    "all" | "article" | "resource"
  >("all");
  const [sortBy, setSortBy] = useState<"date" | "title">("date");

  useEffect(() => {
    async function fetchLinks() {
      try {
        const fetchedLinks = await getLinks();
        setLinks(fetchedLinks);
      } catch (err) {
        setError("Failed to fetch links");
      } finally {
        setLoading(false);
      }
    }
    fetchLinks();
  }, []);

  const handleDelete = async (linkId: number) => {
    if (
      window.confirm("Êtes-vous sûr de vouloir supprimer cette ressource ?")
    ) {
      try {
        await deleteLink(linkId);
        setLinks(links.filter((link) => link.id !== linkId));
      } catch (err) {
        alert("Erreur lors de la suppression");
      }
    }
  };

  // tous les tags uniques
  const allTags = useMemo(() => {
    const tagsSet = new Set<string>();
    links.forEach((link) => {
      link.tags?.forEach((tag) => tagsSet.add(tag));
    });
    return Array.from(tagsSet).sort();
  }, [links]);

  const filteredLinks = useMemo(() => {
    let filtered = links;

    // Recherche par titre description URL
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (link) =>
          link.title?.toLowerCase().includes(query) ||
          link.description?.toLowerCase().includes(query) ||
          link.url.toLowerCase().includes(query)
      );
    }

    // Filtre par tags
    if (selectedTags.length > 0) {
      filtered = filtered.filter((link) =>
        selectedTags.some((tag) => link.tags?.includes(tag))
      );
    }

    // Filtrer par type de ressource
    if (resourceTypeFilter !== "all") {
      filtered = filtered.filter(
        (link) => link.resource_type === resourceTypeFilter
      );
    }

    filtered.sort((a, b) => {
      if (sortBy === "date") {
        return (
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      } else {
        return (a.title || "").localeCompare(b.title || "");
      }
    });

    return filtered;
  }, [links, searchQuery, selectedTags, resourceTypeFilter, sortBy]);

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-4xl font-black uppercase tracking-tighter animate-pulse">
          Loading_Data...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="neo-box p-8 bg-red-50 border-red-500">
          <h2 className="text-2xl text-[var(--accent-primary)] mb-2">
            SYSTEM ERROR
          </h2>
          <p className="font-mono">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20">
      {/* Header */}
      <div className="border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="container mx-auto px-6 py-6 max-w-7xl">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1
                className="text-5xl md:text-7xl mb-2 tracking-tighter"
                style={{ textShadow: "3px 3px 0px rgba(0,0,0,0.1)" }}
              >
                KNOWLEDGE
                <br />
                INGESTER
              </h1>
              <p className="font-mono text-sm bg-black text-white inline-block px-2 py-1">
                v2.0 // ARCHIVE_MODE
              </p>
            </div>
            <div className="text-right hidden md:block">
              <div className="text-6xl font-black leading-none">
                {links.length}
              </div>
              <div className="font-mono text-xs uppercase tracking-widest border-t-2 border-black pt-1 mt-1">
                Total Items
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container relative mx-auto px-6 py-12 max-w-7xl">
        {/* Search Bar */}
        <div className="mb-12 animate-reveal">
          <div className="relative">
            <input
              type="text"
              placeholder="SEARCH_DATABASE..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="neo-input w-full pl-6 pr-6 py-6 text-xl uppercase placeholder:text-gray-300"
            />
            <div className="absolute right-6 top-1/2 transform -translate-y-1/2 pointer-events-none">
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="square"
                  strokeLinejoin="miter"
                  strokeWidth={3}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div
          className="mb-16 animate-reveal"
          style={{ animationDelay: "0.1s" }}
        >
          <div className="flex flex-col lg:flex-row gap-8 items-start">
            {/* Type Filter */}
            <div className="flex-1 w-full">
              <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
                <span className="w-3 h-3 bg-[var(--accent-primary)]"></span>
                FILTER_BY_TYPE
              </h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => setResourceTypeFilter("all")}
                  className={`px-6 py-3 font-bold border-2 border-black transition-all ${
                    resourceTypeFilter === "all"
                      ? "bg-black text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)]"
                      : "bg-white hover:bg-gray-50"
                  }`}
                >
                  ALL
                </button>
                <button
                  onClick={() => setResourceTypeFilter("article")}
                  className={`px-6 py-3 font-bold border-2 border-black transition-all ${
                    resourceTypeFilter === "article"
                      ? "bg-[var(--accent-secondary)] text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
                      : "bg-white hover:bg-gray-50"
                  }`}
                >
                  ARTICLES
                </button>
                <button
                  onClick={() => setResourceTypeFilter("resource")}
                  className={`px-6 py-3 font-bold border-2 border-black transition-all ${
                    resourceTypeFilter === "resource"
                      ? "bg-[var(--accent-primary)] text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
                      : "bg-white hover:bg-gray-50"
                  }`}
                >
                  RESOURCES
                </button>
              </div>
            </div>

            {/* Sort */}
            <div className="w-full lg:w-auto">
              <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
                <span className="w-3 h-3 bg-[var(--accent-secondary)]"></span>
                SORT_ORDER
              </h3>
              <div className="flex gap-3">
                <button
                  onClick={() => setSortBy("date")}
                  className={`px-6 py-3 font-bold border-2 border-black transition-all ${
                    sortBy === "date"
                      ? "bg-black text-white"
                      : "bg-white hover:bg-gray-50"
                  }`}
                >
                  DATE
                </button>
                <button
                  onClick={() => setSortBy("title")}
                  className={`px-6 py-3 font-bold border-2 border-black transition-all ${
                    sortBy === "title"
                      ? "bg-black text-white"
                      : "bg-white hover:bg-gray-50"
                  }`}
                >
                  A-Z
                </button>
              </div>
            </div>
          </div>

          {/* Tags */}
          {allTags.length > 0 && (
            <div className="mt-8 pt-8 border-t-2 border-dashed border-gray-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold">TAG_CLOUD</h3>
                {selectedTags.length > 0 && (
                  <button
                    onClick={() => setSelectedTags([])}
                    className="text-xs font-bold underline hover:text-[var(--accent-primary)]"
                  >
                    CLEAR_SELECTION [{selectedTags.length}]
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                {allTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={`neo-tag px-3 py-1 text-xs uppercase ${
                      selectedTags.includes(tag)
                        ? "bg-black text-white"
                        : "bg-white hover:bg-gray-100"
                    }`}
                  >
                    #{tag}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Results count */}
        <div
          className="mb-8 flex items-center justify-between border-b-2 border-black pb-2 animate-reveal"
          style={{ animationDelay: "0.2s" }}
        >
          <div className="font-mono text-sm">
            DISPLAYING <span className="font-bold">{filteredLinks.length}</span>{" "}
            RECORDS
          </div>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredLinks.map((link, index) => (
            <div
              key={link.id}
              className="neo-box group flex flex-col h-full animate-reveal"
              style={{
                animationDelay: `${0.2 + index * 0.05}s`,
              }}
            >
              <div className="p-6 flex-1 flex flex-col">
                <div className="flex justify-between items-start mb-4 gap-4">
                  <span
                    className={`text-xs font-bold px-2 py-1 border-2 border-black uppercase ${
                      link.resource_type === "resource"
                        ? "bg-[var(--accent-primary)] text-white"
                        : "bg-[var(--accent-secondary)] text-white"
                    }`}
                  >
                    {link.resource_type === "resource" ? "TOOL" : "READ"}
                  </span>
                  <span className="font-mono text-xs text-gray-500">
                    {new Date(link.created_at).toLocaleDateString("en-GB")}
                  </span>
                </div>

                <h2 className="text-2xl font-bold leading-tight mb-4 group-hover:underline decoration-2 underline-offset-4">
                  {link.title}
                </h2>

                <p className="font-mono text-sm text-gray-600 mb-6 flex-1 leading-relaxed">
                  {link.description}
                </p>

                <div className="flex flex-wrap gap-2 mb-6">
                  {link.tags?.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="text-xs font-bold bg-gray-100 px-2 py-1 border border-black"
                    >
                      #{tag}
                    </span>
                  ))}
                  {link.tags && link.tags.length > 3 && (
                    <span className="text-xs font-bold px-1 py-1">
                      +{link.tags.length - 3}
                    </span>
                  )}
                </div>

                <div className="mt-auto pt-4 border-t-2 border-black flex items-center justify-between gap-4">
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-bold text-sm hover:bg-[var(--accent-secondary)] hover:text-white px-2 py-1 -ml-2 transition-colors truncate max-w-[60%]"
                  >
                    OPEN_LINK ↗
                  </a>
                  <button
                    onClick={() => handleDelete(link.id)}
                    className="text-xs font-bold text-red-500 hover:bg-red-500 hover:text-white px-2 py-1 transition-colors"
                  >
                    DELETE
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredLinks.length === 0 && (
          <div className="neo-box p-12 text-center bg-gray-50">
            <div className="text-6xl mb-4">∅</div>
            <h3 className="text-2xl font-bold mb-2">NO_DATA_FOUND</h3>
            <p className="font-mono text-sm">
              Adjust search parameters to retrieve records.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
