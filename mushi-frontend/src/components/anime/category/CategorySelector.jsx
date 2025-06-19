// mushi-frontend/src/components/anime/category/CategorySelector.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { categoryGroups } from '@/services/categories';

const CategorySection = ({ title, items }) => (
    <div className="mb-10 p-6 bg-white/5 backdrop-blur-md rounded-2xl shadow-lg border border-white/10">
        <h3 className="text-2xl font-bold mb-4 text-pink-300 border-b-2 border-pink-400/30 pb-2">{title}</h3>
        <div className="flex flex-wrap gap-3">
            {items.map(item => (
                <Link
                    key={item.slug}
                    to={`/search?category=${item.slug}&title=${encodeURIComponent(item.name)}`}
                    className="bg-neutral-800 text-gray-300 hover:bg-purple-600 hover:text-white px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 shadow-md transform hover:scale-105"
                >
                    {item.name}
                </Link>
            ))}
        </div>
    </div>
);

function CategorySelector() {
    const azListItems = [
        { slug: 'az-list/other', name: '#' },
        { slug: 'az-list/0-9', name: '0-9' },
        ...Array.from({ length: 26 }, (_, i) => ({
            slug: `az-list/${String.fromCharCode(65 + i).toLowerCase()}`,
            name: String.fromCharCode(65 + i)
        }))
    ];

    return (
        <div className="w-full mt-8">
            <CategorySection title={categoryGroups.main.title} items={categoryGroups.main.items} />
            <CategorySection title={categoryGroups.standard.title} items={categoryGroups.standard.items} />
            <CategorySection title={categoryGroups.genres.title} items={categoryGroups.genres.items} />
            <CategorySection title="A-Z List" items={azListItems} />
        </div>
    );
}

export default CategorySelector;
