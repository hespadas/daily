"use client";

import {useEffect, useState} from "react";
import api from "../../lib/api";
import ExperienceModal, {ExperienceData} from "./ExperienceModal";

export default function Experience() {
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [isEditOpen, setIsEditOpen] = useState(false);
    const [editData, setEditData] = useState<ExperienceData | null>(null);
    const [experiences, setExperiences] = useState<ExperienceData[]>([]);

    async function handleEditClick(id: number) {
        try {
            const response = await api.get<ExperienceData>(`/experiences/${id}`);
            setEditData(response.data);
            setIsEditOpen(true);
        } catch (error) {
            console.error("Error fetching experience for edit:", error);
        }
    }

    async function handleDeleteClick(id: number) {
        try {
            await api.delete(`/experiences/${id}`);
            setExperiences(exps => exps.filter(exp => exp.id !== id));
        } catch (error) {
            console.error("Error deleting experience:", error);
        }
    }

    useEffect(() => {
        api.get<ExperienceData[]>("/experiences")
            .then(res => setExperiences(res.data))
            .catch(err => console.error("Error fetching experiences:", err));
    }, []);

    return (
        <section className="flex flex-col items-center justify-center min-h-screen bg-gray-100 px-4">
            <h1 className="text-4xl font-bold mb-6 text-gray-900">Experiences</h1>
            <div className="w-full max-w-2xl space-y-6">
                {experiences.length > 0 ? (
                    experiences.map(exp => (
                        <div key={exp.id} className="relative p-6 bg-white rounded-lg shadow-md border border-gray-200">
                            <button
                                onClick={() => handleDeleteClick(exp.id)}
                                className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 cursor-pointer"
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-6 w-6"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                            <h2 className="text-xl font-semibold text-gray-800">{exp.title}</h2>
                            <p className="text-gray-700 font-medium mt-1">Company: {exp.company}</p>
                            <p className="text-gray-800 my-2">{exp.description}</p>
                            <div className="flex flex-col mt-3 text-sm">
                                <p className="text-gray-600">
                                    Start date: <span className="font-medium">{exp.start_date}</span>
                                </p>
                                <p className="text-gray-600">
                                    End date: <span className="font-medium">{exp.end_date}</span>
                                </p>
                            </div>
                            <button
                                onClick={() => handleEditClick(exp.id)}
                                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                            >
                                Edit Experience
                            </button>
                        </div>
                    ))
                ) : (
                    <p className="text-gray-700 text-center py-8">No experiences found.</p>
                )}
            </div>
            <button
                onClick={() => setIsCreateOpen(true)}
                className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
                Add Experience
            </button>

            {isCreateOpen && (
                <ExperienceModal
                    onClose={() => setIsCreateOpen(false)}
                    onSubmit={data =>
                        api.post("/experiences", data).then(res =>
                            setExperiences(exps => [...exps, res.data])
                        )
                    }
                />
            )}

            {isEditOpen && editData && (
                <ExperienceModal
                    initialData={editData}
                    onClose={() => setIsEditOpen(false)}
                    onSubmit={data =>
                        api.put(`/experiences/${data.id}`, data).then(res =>
                            setExperiences(exps =>
                                exps.map(exp => (exp.id === res.data.id ? res.data : exp))
                            )
                        )
                    }
                />

            )}
        </section>
    );
}
