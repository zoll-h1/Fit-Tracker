import { useState } from 'react';
import { BookmarkPlus, X } from 'lucide-react';
import { templatesApi } from '@/api/templates';

interface Props {
  workoutId: number;
}

export default function SaveAsTemplateButton({ workoutId }: Props) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    if (!name.trim()) return;
    setLoading(true);
    setError('');
    try {
      await templatesApi.saveAsTemplate(workoutId, {
        name: name.trim(),
        description: description || undefined,
        is_public: isPublic,
      });
      setSuccess(true);
      setTimeout(() => {
        setOpen(false);
        setSuccess(false);
        setName('');
        setDescription('');
        setIsPublic(false);
      }, 1500);
    } catch {
      setError('Failed to save template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 border border-slate-600 text-slate-300 hover:text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      >
        <BookmarkPlus className="w-4 h-4" />
        Save as Template
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-sm">
            <div className="flex items-center justify-between p-5 border-b border-slate-700">
              <h2 className="text-base font-bold text-white">Save as Template</h2>
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-5 space-y-3">
              {success ? (
                <p className="text-green-400 text-sm text-center py-4">✓ Template saved!</p>
              ) : (
                <>
                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Template Name *</label>
                    <input
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500"
                      value={name}
                      onChange={e => setName(e.target.value)}
                      placeholder="e.g. Push Day"
                      autoFocus
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Description</label>
                    <textarea
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-violet-500 resize-none"
                      rows={2}
                      value={description}
                      onChange={e => setDescription(e.target.value)}
                      placeholder="Optional"
                    />
                  </div>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <div
                      onClick={() => setIsPublic(p => !p)}
                      className={`w-10 h-6 rounded-full transition-colors relative cursor-pointer ${isPublic ? 'bg-violet-600' : 'bg-slate-600'}`}
                    >
                      <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${isPublic ? 'left-5' : 'left-1'}`} />
                    </div>
                    <span className="text-sm text-slate-300">Make public</span>
                  </label>

                  {error && <p className="text-red-400 text-xs">{error}</p>}
                </>
              )}
            </div>

            {!success && (
              <div className="flex gap-3 p-5 border-t border-slate-700">
                <button
                  onClick={() => setOpen(false)}
                  className="flex-1 bg-slate-700 hover:bg-slate-600 text-white rounded-lg py-2 text-sm font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={!name.trim() || loading}
                  className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white rounded-lg py-2 text-sm font-medium transition-colors"
                >
                  {loading ? 'Saving…' : 'Save'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
