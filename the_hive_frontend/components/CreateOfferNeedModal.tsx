import { useState } from 'react';
import { X, MapPin } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Checkbox } from './ui/checkbox';
import { Badge } from './ui/badge';
import { Calendar } from './ui/calendar';
import { toast } from 'sonner';

interface CreateOfferNeedModalProps {
  open: boolean;
  onClose: () => void;
}

export default function CreateOfferNeedModal({ open, onClose }: CreateOfferNeedModalProps) {
  const [type, setType] = useState<'offer' | 'need'>('offer');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [isRemote, setIsRemote] = useState(false);
  const [capacity, setCapacity] = useState(1);
  const [selectedDates, setSelectedDates] = useState<Date[]>([]);

  const handleAddTag = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagInput.trim())) {
        setTags([...tags, tagInput.trim()]);
      }
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove));
  };

  const handleSubmit = () => {
    if (!title.trim() || !description.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    toast.success(
      type === 'offer' ? 'Offer posted successfully!' : 'Need posted successfully!'
    );
    onClose();
    
    // Reset form
    setTitle('');
    setDescription('');
    setTags([]);
    setIsRemote(false);
    setCapacity(1);
    setSelectedDates([]);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Post</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Type Selector */}
          <div>
            <Label>Type</Label>
            <RadioGroup value={type} onValueChange={(v) => setType(v as 'offer' | 'need')} className="flex gap-4 mt-2">
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="offer" id="offer" />
                <Label htmlFor="offer" className="cursor-pointer">I want to Offer</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="need" id="need" />
                <Label htmlFor="need" className="cursor-pointer">I have a Need</Label>
              </div>
            </RadioGroup>
          </div>

          {/* Title */}
          <div>
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              placeholder="e.g., Web Development Tutoring"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-2"
            />
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              placeholder="Describe what you're offering or what you need..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="mt-2"
            />
          </div>

          {/* Tags */}
          <div>
            <Label htmlFor="tags">Tags</Label>
            <Input
              id="tags"
              placeholder="Press Enter to add tags"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleAddTag}
              className="mt-2"
            />
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="gap-1">
                    {tag}
                    <X
                      className="w-3 h-3 cursor-pointer"
                      onClick={() => handleRemoveTag(tag)}
                    />
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Location */}
          <div>
            <Label>Location</Label>
            <div className="mt-2 space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="remote"
                  checked={isRemote}
                  onCheckedChange={(checked) => setIsRemote(checked as boolean)}
                />
                <Label htmlFor="remote" className="cursor-pointer">
                  This is a remote service
                </Label>
              </div>

              {!isRemote && (
                <div className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex items-center gap-2 text-gray-500 mb-2">
                    <MapPin className="w-4 h-4" />
                    <span className="text-sm">Click on map to set location</span>
                  </div>
                  <div className="w-full h-48 bg-gray-200 rounded flex items-center justify-center">
                    <span className="text-gray-400">Interactive map placeholder</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Capacity */}
          <div>
            <Label htmlFor="capacity">Capacity</Label>
            <Input
              id="capacity"
              type="number"
              min={1}
              value={capacity}
              onChange={(e) => setCapacity(parseInt(e.target.value) || 1)}
              className="mt-2"
            />
            <p className="text-sm text-gray-500 mt-1">
              How many people can participate?
            </p>
          </div>

          {/* Availability (Offers only) */}
          {type === 'offer' && (
            <div>
              <Label>Availability Calendar</Label>
              <div className="mt-2 border rounded-lg p-4">
                <Calendar
                  mode="multiple"
                  selected={selectedDates}
                  onSelect={(dates) => setSelectedDates(dates || [])}
                  className="rounded-md"
                />
                {selectedDates.length > 0 && (
                  <div className="mt-3 text-sm text-gray-600">
                    {selectedDates.length} date(s) selected
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t">
            <Button onClick={onClose} variant="outline" className="flex-1">
              Cancel
            </Button>
            <Button onClick={handleSubmit} className="flex-1">
              Post
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
