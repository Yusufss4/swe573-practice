/**
 * Tags Hierarchy Visualization Page
 * 
 * Displays all semantic tags in hierarchical tree structure.
 * Features: tree view, tag details, usage counts, synonyms.
 * 
 * SRS FR-8.4: Browse tag taxonomy for discovery
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Collapse,
  IconButton,
  Stack,
  TextField,
  Alert,
  CircularProgress,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Search as SearchIcon,
  LocalOffer as TagIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

interface TagSimple {
  id: number;
  name: string;
  description: string | null;
}

interface TagFull {
  id: number;
  name: string;
  description: string | null;
  aliases: string[];
  parent_id: number | null;
  usage_count: number;
  created_at: string;
  updated_at: string;
  parent: TagSimple | null;
  children: TagSimple[];
  synonyms: TagSimple[];
}

interface TagTree {
  id: number;
  name: string;
  description: string | null;
  aliases: string[];
  usage_count: number;
  children: TagTree[];
}

// Recursive tree node component
const TagNode: React.FC<{
  tag: TagTree;
  depth: number;
  searchFilter: string;
  onTagClick: (tagId: number) => void;
  selectedTagId: number | null;
}> = ({ tag, depth, searchFilter, onTagClick, selectedTagId }) => {
  const [expanded, setExpanded] = useState(depth < 2); // Auto-expand first 2 levels

  // Search filter logic
  const matchesSearch = searchFilter === '' || 
    tag.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
    (tag.description && tag.description.toLowerCase().includes(searchFilter.toLowerCase())) ||
    tag.aliases.some(a => a.toLowerCase().includes(searchFilter.toLowerCase()));

  const hasMatchingChild = (node: TagTree): boolean => {
    if (node.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
        (node.description && node.description.toLowerCase().includes(searchFilter.toLowerCase())) ||
        node.aliases.some(a => a.toLowerCase().includes(searchFilter.toLowerCase()))) {
      return true;
    }
    return node.children.some(child => hasMatchingChild(child));
  };

  const shouldShow = searchFilter === '' || matchesSearch || tag.children.some(hasMatchingChild);

  if (!shouldShow) return null;

  const hasChildren = tag.children.length > 0;
  const isSelected = selectedTagId === tag.id;

  return (
    <Box sx={{ ml: depth * 3 }}>
      <Card
        sx={{
          mb: 1,
          bgcolor: isSelected ? 'action.selected' : 'background.paper',
          cursor: 'pointer',
          '&:hover': { bgcolor: 'action.hover' },
        }}
        onClick={() => onTagClick(tag.id)}
      >
        <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
          <Stack direction="row" spacing={1} alignItems="center">
            {hasChildren && (
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  setExpanded(!expanded);
                }}
              >
                {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            )}
            {!hasChildren && <Box sx={{ width: 40 }} />}
            
            <TagIcon fontSize="small" color="primary" />
            
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="subtitle1" fontWeight={depth === 0 ? 'bold' : 'medium'}>
                {tag.name}
              </Typography>
              {tag.description && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {tag.description}
                </Typography>
              )}
              
              <Stack direction="row" spacing={1} sx={{ mt: 1 }} flexWrap="wrap">
                {tag.aliases.map((alias, idx) => (
                  <Chip
                    key={idx}
                    label={alias}
                    size="small"
                    variant="outlined"
                    sx={{ mb: 0.5 }}
                  />
                ))}
                <Chip
                  label={`Used ${tag.usage_count}x`}
                  size="small"
                  color={tag.usage_count > 0 ? 'success' : 'default'}
                  sx={{ mb: 0.5 }}
                />
              </Stack>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Collapse in={expanded && hasChildren}>
        {tag.children.map((child) => (
          <TagNode
            key={child.id}
            tag={child}
            depth={depth + 1}
            searchFilter={searchFilter}
            onTagClick={onTagClick}
            selectedTagId={selectedTagId}
          />
        ))}
      </Collapse>
    </Box>
  );
};

// Tag detail sidebar
const TagDetail: React.FC<{ tagId: number }> = ({ tagId }) => {
  const { data: tag, isLoading, error } = useQuery<TagFull>({
    queryKey: ['tag', tagId],
    queryFn: async () => {
      const response = await api.get(`/tags/${tagId}`);
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !tag) {
    return <Alert severity="error">Failed to load tag details</Alert>;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          <TagIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          {tag.name}
        </Typography>

        {tag.description && (
          <Typography variant="body1" color="text.secondary" paragraph>
            {tag.description}
          </Typography>
        )}

        <Divider sx={{ my: 2 }} />

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Aliases
          </Typography>
          {tag.aliases.length > 0 ? (
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {tag.aliases.map((alias, idx) => (
                <Chip key={idx} label={alias} size="small" sx={{ mb: 0.5 }} />
              ))}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No aliases
            </Typography>
          )}
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Usage Count
          </Typography>
          <Chip
            label={`${tag.usage_count} offers/needs`}
            color={tag.usage_count > 0 ? 'success' : 'default'}
          />
        </Box>

        {tag.parent && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Parent Tag
            </Typography>
            <Chip
              label={tag.parent.name}
              icon={<TagIcon />}
              variant="outlined"
              color="primary"
            />
          </Box>
        )}

        {tag.children.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Child Tags
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {tag.children.map((child) => (
                <Chip
                  key={child.id}
                  label={child.name}
                  icon={<TagIcon />}
                  size="small"
                  variant="outlined"
                  sx={{ mb: 0.5 }}
                />
              ))}
            </Stack>
          </Box>
        )}

        {tag.synonyms.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Synonyms
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {tag.synonyms.map((syn) => (
                <Tooltip key={syn.id} title={syn.description || ''}>
                  <Chip
                    label={syn.name}
                    size="small"
                    color="secondary"
                    variant="outlined"
                    sx={{ mb: 0.5 }}
                  />
                </Tooltip>
              ))}
            </Stack>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        <Typography variant="caption" color="text.secondary" display="block">
          Created: {new Date(tag.created_at).toLocaleDateString()}
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block">
          Updated: {new Date(tag.updated_at).toLocaleDateString()}
        </Typography>
      </CardContent>
    </Card>
  );
};

// Main component
const TagsPage: React.FC = () => {
  const [searchFilter, setSearchFilter] = useState('');
  const [selectedTagId, setSelectedTagId] = useState<number | null>(null);

  const { data: tagTree, isLoading, error } = useQuery<TagTree[]>({
    queryKey: ['tags-tree'],
    queryFn: async () => {
      const response = await api.get('/tags/tree');
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Failed to load tags hierarchy</Alert>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Tags Hierarchy
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Browse all tags organized by category. Click on a tag to see detailed information including
        parent-child relationships, synonyms, and usage statistics.
      </Typography>

      <TextField
        fullWidth
        placeholder="Search tags by name, description, or alias..."
        value={searchFilter}
        onChange={(e) => setSearchFilter(e.target.value)}
        InputProps={{
          startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
        }}
        sx={{ mb: 3 }}
      />

      <Stack direction="row" spacing={3}>
        <Box sx={{ flex: 2 }}>
          {tagTree && tagTree.length > 0 ? (
            tagTree.map((rootTag) => (
              <TagNode
                key={rootTag.id}
                tag={rootTag}
                depth={0}
                searchFilter={searchFilter}
                onTagClick={setSelectedTagId}
                selectedTagId={selectedTagId}
              />
            ))
          ) : (
            <Alert severity="info">No tags found matching your search</Alert>
          )}
        </Box>

        {selectedTagId && (
          <Box sx={{ flex: 1, position: 'sticky', top: 80, alignSelf: 'flex-start' }}>
            <TagDetail tagId={selectedTagId} />
          </Box>
        )}
      </Stack>
    </Box>
  );
};

export default TagsPage;
